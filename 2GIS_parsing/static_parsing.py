import requests
import re
from bs4 import BeautifulSoup
from building_types import building_type_keywords

url = "https://2gis.ru/moscow/firm/70000001031354947/38.073195%2C55.546556?m=38.06754%2C55.547161%2F15.67"
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

print("Тип здания:", building_type or "не определен")

floor_pattern = re.compile(r'\bэтаж[а-яё]*\b', re.IGNORECASE)
    
found_elements = [
    element for element in soup.find_all(string=floor_pattern)
    if element.strip()
]

if found_elements:
    for text in found_elements:
        print(f"Количество этажей: {text.strip()}")
else:
    print("Упоминания этажности не найдены")


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

print("Количество подъездов:", number_of_entrances or "не определено")
