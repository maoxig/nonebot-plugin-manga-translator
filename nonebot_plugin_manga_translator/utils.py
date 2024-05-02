import httpx
import uuid
import base64
import random
from hashlib import md5
from PIL import Image
from io import BytesIO
from nonebot import logger
import asyncio
import time
import json
import datetime
import hashlib
import hmac
from urllib.parse import quote
from typing import Tuple, Union
from .config import Config
class MangaTranslator:

    def __init__(self, Config:Config) -> None:
        self.config = Config
        self.img_url = []
        self.api = []
        if self.config.youdao_app_key:
            self.api.append(self.youdao)
            logger.info("检测到有道API")
        if self.config.baidu_app_id:
            self.api.append(self.baidu)
            logger.info("检测到百度API")
        if self.config.offline_url:
            self.api.append(self.offline)
            logger.info("检测到离线模型")
        if self.config.huoshan_access_key_id:
            self.api.append(self.huoshan)
            logger.info("检测到火山API")

    async def call_api(self, image_bytes:bytes)->Tuple[Union[None,bytes],str]:
        for api in self.api:
            try:
                result = await api(image_bytes)
                return result
            except httpx.HTTPError as e:
                logger.warning(f"API[{api.__name__}]不可用：{e}尝试切换下一个")
        return None, "无可用API"

    async def youdao(self, image_bytes) -> Tuple[bytes, str]:
        """有道翻译"""
        salt = str(uuid.uuid1())
        data = {
            "from": "auto",
            "to": "zh-CHS",
            "type": "1",
            "appKey": self.config.youdao_app_key,
            "salt": salt,
            "render": 1,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            if len(image_bytes) >= 2 * 1024 * 1024:
                image_bytes = self.compress_image(image_bytes)
            q = base64.b64encode(image_bytes).decode("utf-8")
            data["q"] = q
            signStr = (
                self.config.youdao_app_key + q + salt + self.config.youdao_app_secret
            )
            sign = self.encrypt(signStr)
            data["sign"] = sign
            youdao_res = await client.post(
                url="https://openapi.youdao.com/ocrtransapi", data=data, headers=headers
            )
            img_base64 = youdao_res.json()["render_image"]
            pic = base64.b64decode(img_base64)
        return pic, "有道"

    async def baidu(self, image_bytes:bytes)->Tuple[bytes,str]:
        """百度翻译"""
        async with httpx.AsyncClient() as client:
            salt = random.randint(32768, 65536)
            image_data = image_bytes
            image_size = len(image_data)
            if image_size >= 4 * 1024 * 1024:
                logger.info("图片过大，进行压缩")
                image_data = self.compress_image(image_data)
            sign = md5(
                (
                    self.config.baidu_app_id
                    + md5(image_data).hexdigest()
                    + str(salt)
                    + "APICUID"
                    + "mac"
                    + self.config.baidu_app_key
                ).encode("utf-8")
            ).hexdigest()
            payload = {
                "from": "auto",
                "to": "zh",
                "appid": self.config.baidu_app_id,
                "salt": salt,
                "sign": sign,
                "cuid": "APICUID",
                "mac": "mac",
                "paste": 1,
                "version": 3,
            }
            image = {"image": ("image.jpg", image_data, "multipart/form-data")}
            baidu_res = await client.post(
                url="http://api.fanyi.baidu.com/api/trans/sdk/picture",
                params=payload,
                files=image,
            )
            img_base64 = baidu_res.json()["data"]["pasteImg"]
            pic = base64.b64decode(img_base64)
        return pic, "百度"

    async def offline(self, image_bytes:bytes, timeout=60)->Tuple[Union[None,bytes],str]:
        """离线翻译,这里写的有点烂，求pr"""
        async with httpx.AsyncClient() as client:
            img_content = image_bytes
            form = {"file": ("image.png", img_content, "image/png")}
            response = await client.post(
                self.config.offline_url + "/submit",
                files=form,
                data={"translator": "offline"},
            )  # 改为本地翻译器
            # 这里的填写请参考文档，根据自己情况填写，例如data={"translator":"youdao","tgt_lang":"CHS"},如果是有道、百度、gpt等，请确保填写了key
            response.raise_for_status()  # 检查响应状态
            task_id = response.json()["task_id"]
            req = {"taskid": task_id}
            # 轮询获取翻译结果，超时时间为60s
            async def check_translation_result() -> Tuple[Union[None, bytes], str]:
                start_time = time.monotonic()
                while True:
                    response = await client.get(
                        self.config.offline_url + "/task-state", params=req
                    )
                    response.raise_for_status()
                    state = response.json()["state"]
                    finished = response.json()["finished"]
                    if state == "finished" or finished:
                        break
                    if time.monotonic() - start_time > timeout:
                        return None, "超时"
                    await asyncio.sleep(1)

                img_data = await client.get(
                    url=self.config.offline_url + "/result/" + task_id
                )
                if img_data.status_code == 200 and img_data.content:
                    return img_data.content, "离线"
                else:
                    return None, "离线"

            return await check_translation_result()

    async def huoshan(self, image_bytes:bytes)->Tuple[bytes,str]:
        """火山引擎翻译，构建签名"""
        async with httpx.AsyncClient() as client:
            data = json.dumps(
                {
                    "Image": str(base64.b64encode(image_bytes), encoding="utf-8"),
                    "TargetLanguage": "zh",
                }
            )
            x_content_sha256 = self.hash_sha256(data)
            now_time = datetime.datetime.utcnow()  #
            x_date = now_time.strftime("%Y%m%dT%H%M%SZ")
            credential_scope = "/".join(
                [x_date[:8], "cn-north-1", "translate", "request"]
            )
            signed_headers_str = ";".join(
                ["content-type", "host", "x-content-sha256", "x-date"]
            )
            canonical_request_str = "\n".join(
                [
                    "POST",
                    "/",
                    self.norm_query(
                        {"Action": "TranslateImage", "Version": "2020-07-01"}
                    ),
                    "\n".join(
                        [
                            "content-type:" + "application/json",
                            "host:" + "open.volcengineapi.com",
                            "x-content-sha256:" + x_content_sha256,
                            "x-date:" + x_date,
                        ]
                    ),
                    "",
                    signed_headers_str,
                    x_content_sha256,
                ]
            )
            sign_result = {
                "Host": "open.volcengineapi.com",
                "X-Content-Sha256": x_content_sha256,
                "X-Date": x_date,
                "Content-Type": "application/json",
                "Authorization": "HMAC-SHA256 Credential={}, SignedHeaders={}, Signature={}".format(
                    self.config.huoshan_access_key_id + "/" + credential_scope,
                    signed_headers_str,
                    self.hmac_sha256(
                        self.hmac_sha256(
                            self.hmac_sha256(
                                self.hmac_sha256(
                                    self.hmac_sha256(
                                        self.config.huoshan_secret_access_key.encode(
                                            "utf-8"
                                        ),
                                        x_date[:8],
                                    ),
                                    "cn-north-1",
                                ),
                                "translate",
                            ),
                            "request",
                        ),
                        "\n".join(
                            [
                                "HMAC-SHA256",
                                x_date,
                                credential_scope,
                                self.hash_sha256(canonical_request_str),
                            ]
                        ),
                    ).hex(),
                ),
            }
            params = {"Action": "TranslateImage", "Version": "2020-07-01"}
            huoshan_res = await client.post(
                url="https://open.volcengineapi.com/",
                headers=sign_result,
                params=params,
                data=data, # type: ignore
            )
            img_base64 = huoshan_res.json()["Image"]
            pic = base64.b64decode(img_base64)
        return pic, "火山"

    @staticmethod
    def compress_image(image_data: bytes) -> bytes:
        with BytesIO(image_data) as input_buffer:
            with Image.open(input_buffer) as image:
                # image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                output_buffer = BytesIO()
                image.save(output_buffer, format="JPEG", optimize=True, quality=80)
                return output_buffer.getvalue()

    @staticmethod
    def encrypt(signStr):
        hash_algorithm = md5()
        hash_algorithm.update(signStr.encode("utf-8"))
        return hash_algorithm.hexdigest()

    @staticmethod
    def hash_sha256(content: str):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def norm_query(params):
        query = ""
        for key in sorted(params.keys()):
            if isinstance(params[key], list):
                for k in params[key]:
                    query = (
                        query
                        + quote(key, safe="-_.~")
                        + "="
                        + quote(k, safe="-_.~")
                        + "&"
                    )
            else:
                query = (
                    query
                    + quote(key, safe="-_.~")
                    + "="
                    + quote(params[key], safe="-_.~")
                    + "&"
                )
        query = query[:-1]
        return query.replace("+", "%20")

    @staticmethod
    def hmac_sha256(key: bytes, content: str):
        return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


if __name__=="__main__":
    def generate_large_white_image():
        width = 4000
        height = 4000
        image = Image.new("RGB", (width, height), (255, 255, 255))
        output_buffer = BytesIO()
        image.save(output_buffer, format="JPEG")
        return output_buffer.getvalue()

    image_data = generate_large_white_image()
    print("原始图像大小:", len(image_data))

    compressed_data = MangaTranslator.compress_image(image_data)
    print("压缩后图像大小:", len(compressed_data))
