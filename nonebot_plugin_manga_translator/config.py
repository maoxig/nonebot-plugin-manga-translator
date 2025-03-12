from pydantic import BaseModel, validator
from typing import Union


class Config(BaseModel):
    # 百度
    baidu_app_id: Union[str, int] = ""
    baidu_app_key: str = ""

    # 有道
    youdao_app_key: str = ""
    youdao_app_secret: str = ""
    # 离线
    offline_url: str = ""
    offline_api_config: dict = {
        "translator": {
            "no_text_lang_skip": False,
            "target_lang": "CHS",
            "translator": "offline",
        },
    }
    # 火山翻译
    huoshan_access_key_id: str = ""
    huoshan_secret_access_key: str = ""
