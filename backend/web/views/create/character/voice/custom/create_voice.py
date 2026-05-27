import os

import requests


# prefix:前缀,方便找对应的音色
def create_voice(voice_url,prefix):
    headers={#都是阿里云文档定义好的
        'Authorization':f'Bearer{os.getenv('API_KEY')}',
        'Content-Type': 'application/json'
    }
    data={
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            #要搜一下ctrl shift f定义的模型需要一致，给的模板模型不一样
            # 合成时的model 必须等于 复刻时的target_model
            "target_model": "cosyvoice-v3-flash",
            "prefix": prefix,
            "url": voice_url,
            "language_hints": ["zh"]
        }
    }

    response=requests.post(os.getenv('VOICE_URL'),headers=headers,json=data)
    return response.json()