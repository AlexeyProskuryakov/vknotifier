from api.vk import VK_API

__author__ = '4ikist'

api = None

apis = {
    'vk': VK_API
}


def get_api(api_name, login, pwd):
    global api
    if not api:
        api = apis[api_name](login, pwd)

    return api
