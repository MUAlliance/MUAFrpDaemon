import requests
import json
from config import FRPC_UNION_MEMBER_KEY

class UnionAPI:
    def __init__(self, api_root):
        self.__api_root = api_root
        self.__api_root_public = api_root + '/public'

    def queryPublicAPI(self) -> list[dict]:
        response = requests.get(self.__api_root_public)
        # (30/11/2023 kontornl) 增加响应码非 200 以及格式非 JSON 防护
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                raise json.JSONDecodeError('queryPublicAPI() failed caused by not JSON-formatted response')
        else:
            raise Exception(f'queryPublicAPI() failed, HTTP status code {response.status_code}')
    def queryAPI(self) -> list[dict]:
        response = requests.get(self.__api_root, headers={"X-Union-Network-Query-Token" : FRPC_UNION_MEMBER_KEY})
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                raise json.JSONDecodeError('queryAPI() failed caused by not JSON-formatted response')
        else:
            raise Exception(f'queryAPI() failed, HTTP status code {response.status_code}. Invalid FRPC_UNION_MEMBER_KEY?')