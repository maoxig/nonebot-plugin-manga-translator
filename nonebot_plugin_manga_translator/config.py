from pydantic import BaseModel
from typing import Union


class Config(BaseModel):
    # 百度
    baidu_app_id: Union[str, int]
    baidu_app_key: str = ""

    # 有道
    youdao_app_key: str = ""
    youdao_app_secret: str = ""
    # 离线
    offline_url: str = ""
    offline_api_data: dict = {"translator": "youdao", "tgt_lang": "CHS"}
    # 火山翻译
    huoshan_access_key_id: str = ""
    huoshan_secret_access_key: str = ""
