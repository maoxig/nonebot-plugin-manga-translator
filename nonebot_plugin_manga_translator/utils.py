import io
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

    def __init__(self, Config: Config) -> None:
        self.config = Config
        self.img_url = []
        self.api = []
        if self.config.youdao_app_key:
            self.api.append(self.youdao)
            logger.info("检测到有道API")

        if self.config.baidu_app_id:
            self.config.baidu_app_id = str(self.config.baidu_app_id)  # 兼容int
            self.api.append(self.baidu)
            logger.info("检测到百度API")

        if self.config.offline_url:
            self.api.append(self.offline)
            logger.info("检测到离线模型")
            logger.info(f"离线请求api_config: {str(self.config.offline_api_config)}")

        if self.config.huoshan_access_key_id:
            self.api.append(self.huoshan)
            logger.info("检测到火山API")

    async def call_api(self, image_bytes: bytes) -> Tuple[Union[None, bytes], str]:
        for api in self.api:
            try:
                result = await api(image_bytes)
                return result
            except httpx.HTTPError as e:
                logger.warning(f"API[{api.__name__}]不可用：{e} 尝试切换下一个")
            except Exception as e:
                logger.error(f"API[{api.__name__}]出现未知错误：{e} 尝试切换下一个")
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
            if "render_image" not in youdao_res.json():
                logger.error(youdao_res.json())
                raise ValueError("有道API返回错误: " + str(youdao_res.json()))
            img_base64 = youdao_res.json()["render_image"]
            pic = base64.b64decode(img_base64)
        return pic, "有道"

    async def baidu(self, image_bytes: bytes) -> Tuple[bytes, str]:
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
            if "data" not in baidu_res.json():
                logger.error(baidu_res.json())
                raise ValueError("百度API返回错误: " + str(baidu_res.json()))
            img_base64 = baidu_res.json()["data"]["pasteImg"]
            pic = base64.b64decode(img_base64)
        return pic, "百度"

    async def offline(
        self, image_bytes: bytes, timeout=60
    ) -> Tuple[Union[None, bytes], str]:
        """离线翻译"""
        # 提交任务
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                form = {"image": ("image.png", image_bytes, "image/png")}
                response = await client.post(
                    self.config.offline_url + "/translate/with-form/image/stream",
                    files=form,
                    data={"config": json.dumps(self.config.offline_api_config)},
                )

            response.raise_for_status()  # 检查响应状态

            if response.status_code !=200:
                logger.error(f"离线API请求出现错误：code:{response.status_code}, text:{response.text}")
                return None, "离线"
            buffer = io.BytesIO(response.content)
            output_images = []  # 保存所有结果图片
            while True:
                # 读取状态码（1字节）
                status_byte = buffer.read(1)
                if not status_byte:
                    break
                status = int.from_bytes(status_byte, byteorder="big")
                # 读取数据长度（4字节，大端序）
                size_bytes = buffer.read(4)
                if len(size_bytes) < 4:
                    logger.error("数据长度不完整")
                    break
                data_size = int.from_bytes(size_bytes, byteorder="big")
                # 读取数据内容
                data = buffer.read(data_size)
                if len(data) < data_size:
                    logger.error(f"数据不完整，期望 {data_size} 字节，实际 {len(data)} 字节")
                    break
                if status == 0:
                    output_images.append(data)
                elif status == 1:
                    # 进度更新
                    logger.info(f"进度更新：{data.decode('utf-8')}")
                elif status == 2:
                    # 错误信息
                    error_msg = data.decode("utf-8")
                    raise Exception(f"服务器返回错误：{error_msg}")
                elif status == 3:
                    # 等待队列位置：解析为整数
                    logger.info(f"等待队列位置：{int.from_bytes(data, byteorder='big')}")
                elif status == 4:
                    # 等待翻译实例
                    logger.info("等待翻译实例")
            if not output_images:
                logger.error("离线API返回数据为空")
                return None, "离线"
            return output_images[0], "离线"
        except Exception as e:
            logger.error(f"离线API请求出现错误：{e}")
            return None, "离线"

    async def huoshan(self, image_bytes: bytes) -> Tuple[bytes, str]:
        """火山引擎翻译，构建签名"""
        async with httpx.AsyncClient() as client:
            data = json.dumps(
                {
                    "Image": str(base64.b64encode(image_bytes), encoding="utf-8"),
                    "TargetLanguage": "zh",
                }
            )
            x_content_sha256 = self.hash_sha256(data)
            now_time = datetime.datetime.now()  #
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
                data=data,  # type: ignore
            )
            if "Image" not in huoshan_res.json():
                logger.error(huoshan_res.json())
                raise ValueError("火山API返回错误: " + str(huoshan_res.json()))
            img_base64 = huoshan_res.json()["Image"]
            pic = base64.b64decode(img_base64)
        return pic, "火山"

    @staticmethod
    def compress_image(image_data: bytes) -> bytes:
        with BytesIO(image_data) as input_buffer:
            with Image.open(input_buffer) as image:
                if image.mode == "RGBA":
                    image = image.convert("RGB")
                image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
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


if __name__ == "__main__":

    def test_compression(image_path):
        try:
            with open(image_path, "rb") as file:
                image_data = file.read()
            print("原始图像大小:", len(image_data))

            compressed_data = MangaTranslator.compress_image(image_data)
            print("压缩后图像大小:", len(compressed_data))
        except Exception as e:
            print(str(e))
