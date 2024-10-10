class ModelConfig(object):

    def __init__(self,
                 method,
                 model_name,
                 temperature,
                 max_tokens,
                 api_key,
                 base_url,
                 context
                 ):
        self.method = method
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.base_url = base_url
        self.context = context
