import requests


def auto_complete(text):
    url = "http://165.227.224.64:8080/generate?start_text="+text+"&n=1"
    response = requests.get(url)
    return dict(response.json())


print auto_complete("we found ourselves in")