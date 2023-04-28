import httpx
import uuid
import base64
import random
from hashlib import md5
from PIL import Image
from io import BytesIO
from nonebot import logger,get_driver

class MangaTranslator:
    
    def __init__(self) -> None:
        config=get_driver().config
        self.img_url=[]
        self.api=[]
        #百度
        self.baidu_app_id:str=str(getattr(config,"baidu_app_id",""))
        self.baidu_app_key:str=str(getattr(config,"baidu_app_key",""))
        if self.baidu_app_id:
            self.api.append(self.baidu)
    
        #有道
        self.youdao_app_key:str=str(getattr(config,"youdao_app_key",""))
        self.youdao_app_secret:str=str(getattr(config,"youdao_app_secret",""))
        if self.youdao_app_key:
            self.api.append(self.youdao)
    
    async def call_api(self,imageUrl):
        for api in self.api:
            try:
                result=await api(imageUrl)
                return result
            except Exception as e:
                logger.warning(f"API[{api.__name__}]不可用：{e}尝试切换下一个")
        return None,"无可用API"
   
 
    async def youdao(self,imageUrl):
        salt = str(uuid.uuid1())
        data = {'from': 'auto', 'to': 'zh-CHS', 'type': '1',
                'appKey': self.youdao_app_key, 'salt': salt, "render": 1}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with httpx.AsyncClient() as client:
            res=await client.get(imageUrl)
            if len(res.content)>=2*1024*1024:
                res.content=self.compress_image(res.content)
            q=base64.b64encode(res.content).decode("utf-8")
            data['q'] = q
            signStr = self.youdao_app_key + q + salt + self.youdao_app_secret
            sign = self.encrypt(signStr)
            data['sign'] = sign
            youdao_res=await client.post(url='https://openapi.youdao.com/ocrtransapi',data=data,headers=headers)
            img_base64=youdao_res.json()["render_image"]
            pic=base64.b64decode(img_base64)
        return pic,"有道"
    
    
    async def baidu(self,imageUrl):
        async with httpx.AsyncClient() as client:
            res=await client.get(imageUrl)
            salt = random.randint(32768, 65536)
            image_data=res.content
            image_size=len(image_data)
            if image_size>=4*1024*1024:
                logger.info("图片过大，进行压缩")
                image_data=self.compress_image(image_data)
            sign = md5((self.baidu_app_id+md5(image_data).hexdigest()+str(salt)+"APICUID"+"mac"+self.baidu_app_key).encode('utf-8')).hexdigest()
            payload = {'from': "auto", 'to': "zh", 'appid': self.baidu_app_id, 'salt': salt, 'sign': sign, 'cuid': 'APICUID', 'mac': "mac","paste":1,"version":3}
            image = {'image': ("image.jpg",image_data, "multipart/form-data")}
            baidu_res=await client.post(url='http://api.fanyi.baidu.com/api/trans/sdk/picture',params=payload,files=image)
            img_base64=baidu_res.json()["data"]["pasteImg"]
            pic=base64.b64decode(img_base64)
        return pic,"百度"
    
    @staticmethod
    def compress_image(image_data):
        with BytesIO(image_data) as input:
            image=Image.open(input)
            image=image.convert("RGB")
            image=image.resize((int(image.width*0.5),int(image.height*0.5)),Image.ANTIALIAS)
            image.save(input,format="JPEG",quality=80)
            return input.getvalue()
        
    @staticmethod
    def encrypt(signStr):
        hash_algorithm = md5()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()