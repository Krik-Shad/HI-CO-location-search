import requests
import re
from bs4 import BeautifulSoup
from building_types import building_type_keywords

url = "https://2gis.ru/zhukovskiy/firm/70000001028380845/38.087975%2C55.610152?m=38.091059%2C55.609604%2F16.46%2Fr%2F23.65"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


url2 = "https://2gis.ru/zhukovskiy/firm/70000001028380845/38.087975%2C55.610152/tab/inside?m=38.091059%2C55.609604%2F16.46%2Fr%2F23.65"
response2 = requests.get(url2, headers=headers, timeout=10)
soup2 = BeautifulSoup(response2.text, 'html.parser')
orgs = soup2.find_all('div', class_='_1kf6gff')  # Возможный класс для карточек организаций

list = []
for org in orgs:
    name_element = org.find('span', class_='_lvwrwt')  # Класс для названия
    if name_element:
        name = name_element.text.strip()
        list.append(name)

print(list)
print(len(list))
