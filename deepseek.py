from openai import OpenAI

class DeepSeek(OpenAI):
    def __init__(self, api_key: str, base_url="https://api.deepseek.com"):
        super().__init__(api_key=api_key, base_url=base_url)

    def list_deepseek_models(self):
        """
        获取Deepseek模型列表
        """
        return self.models.list()

