import requests
import re
from bs4 import BeautifulSoup
from building_types import building_type_keywords
from url_parsing import url
import csv

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()
    
soup = BeautifulSoup(response.text, 'html.parser')

page_text = soup.find('div', class_='_1tfwnxl').get_text() + soup.find('div', class_='_8sgdp4').get_text()

building_type = None
for keyword in building_type_keywords:
    if keyword.lower() in page_text.lower():
        building_type = keyword
        break

# print("Тип здания:", building_type or "не определен")

floor_pattern = re.compile(r'\bэтаж[а-яё]*\b', re.IGNORECASE)
    
found_elements = [
    element for element in soup.find_all(string=floor_pattern)
    if element.strip()
]

if found_elements:
    for text in found_elements:
        number_of_floors = text.strip()
        # print(f"Количество этажей: {number_of_floors}")

else:
    number_of_floors = None
    # print("Упоминания этажности не найдены")

entrances_pattern = re.compile(
    r'(подъезд[а-яё]*|вход[а-яё]*)\s*:\s*(\d+)|'  
    r'(\d+)\s*(подъезд[а-яё]*|вход[а-яё]*)|',      
    re.IGNORECASE
)

found_entrances = []
for element in soup.find_all(string=entrances_pattern):
    matches = entrances_pattern.findall(element)
    for match in matches:
        found_entrances.append(match)

number_of_entrances = ' '.join(filter(None, max(found_entrances))) if found_entrances else None
# print("Количество подъездов:", number_of_entrances or "не определено")


address = None

address_div = soup.find('div', class_='_13eh3hvq')
if address_div:
    address_link = address_div.find('a', class_='_2lcm958')
    if address_link:
        address = address_link.get_text(strip=True)
        # print(address)

else:

    address_h1 = soup.find('h1', class_='_1x89xo5')

    if address_h1:
        address = address_h1.span.get_text(strip=True)  
        # print(address)

data = [
    ["Адрес", "Тип здания", "Количество этажей", "Количество входов"],
    [address, building_type, number_of_floors, number_of_entrances]
]

with open('2GIS_parsing\\static_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)


# print(data)
