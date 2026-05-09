import base64


with open('./images/gdp_1980_2020.jpg', 'rb') as f:
    b64_image = base64.b64encode(f.read()).decode('utf-8')
    print(b64_image)