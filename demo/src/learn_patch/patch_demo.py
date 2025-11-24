import requests

URL = "https://www.mockaroo.com/"


def fetch_net():
    response = requests.get(URL)
    if response.status_code == 200:
        return "success"
    return "fail"


def parse():
    answer = fetch_net() + str(123)
    return answer
