import requests
import base64

with open('2.png', 'rb') as image_file:
    string = base64.b64encode(image_file.read()).decode('utf-8')

url = "http://127.0.0.1:3000/api"
res = requests.post(url=url, json={"img": string})
print(res.url)
print(res.json())
