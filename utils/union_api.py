import requests
import json
from config import FRPC_UNION_MEMBER_KEY

class UnionAPI:
    def __init__(self, api_root):
        self.__api_root = api_root
        self.__api_root_public = api_root + '/public'

    def queryPublicAPI(self) -> list[dict]:
        response = requests.get(self.__api_root_public)
        return json.loads(response.text)

    def queryAPI(self) -> list[dict]:
        response = requests.get(self.__api_root, headers={"X-Union-Network-Query-Token" : FRPC_UNION_MEMBER_KEY})
        return json.loads(response.text)