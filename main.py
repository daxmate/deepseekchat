#! ./.venv/bin/python3

import requests 
import sys
from openai import OpenAI
import os

mail_content = sys.stdin.read()
# Please install OpenAI SDK first: `pip3 install openai`
deepseek_api_key = ""

with open(os.path.expanduser("~/dotfiles/ai_api_keys")) as f:
    for line in f.readlines():
        _, name_key = line.split() 
        name, key = name_key.split('=')
        if name == "DEEPSEEK_API_KEY":
            deepseek_api_key = key

if deepseek_api_key:
    client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个精通国际商务的资深人士，精通英文、日语及中文" },
            {"role": "user", "content": mail_content + '\n' +   '请专业的回复这封邮件，回复时请用与原文相同的语种，'
             '邮件不需要签名'},
        ],
        stream=False
    )

    print(response.choices[0].message.content)
