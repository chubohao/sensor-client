import requests
import base64

# "server ip and port"
url = 'http://49.235.103.30:8888/'
headers = {'content-type': "application/json"}

with open("test.jpg", "rb") as img:
    string = base64.b64encode(img.read())

data = {"image":string}
respose = requests.post(url, json=data)
print(respose.text)