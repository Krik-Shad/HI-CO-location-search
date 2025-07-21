import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import re
from url_parsing import url

# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Открываем на весь экран
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Инициализация драйвера
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def parse_building_organizations(url, max_orgs=100):
    try:
        driver.get(url)
        time.sleep(3)
        

        try:
            in_building_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a._2lcm958[href*="inside"]'))
            )
            
            in_building_btn.click()
            time.sleep(3)
        except Exception as e:
            print(f"Не удалось найти/кликнуть кнопку 'В здании': {e}")
            return []

        # Находим боковую панель с организациями
        sidebar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div._1rkbbi0x'))
        )
        
        # Прокручиваем боковую панель до кнопки "Добавить организацию"
        last_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
        attempts = 0
        
        while attempts < 10:  # Максимум 10 попыток прокрутки
            # Прокручиваем вниз боковую панель
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
            time.sleep(2)  # Даем время для загрузки
            
            # Проверяем, появилась ли кнопка "Добавить организацию"
            try:
                add_button = driver.find_element(By.CSS_SELECTOR, 'button._m2vlor6')
                # print("Достигнут конец списка организаций")
                break
            except:
                pass
            
            # Проверяем, изменилась ли высота прокрутки
            new_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
            if new_height == last_height:
                attempts += 1
            last_height = new_height
        
        # Парсинг организаций
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        organizations = []
        
        for org in soup.select('div._1kf6gff'):
            try:
                name = org.select_one('span._lvwrwt').get_text(strip=True)
                category = org.select_one('span._oqoid').get_text(strip=True) if org.select_one('span._oqoid') else ""
                rating = org.select_one('div._y10azs').get_text(strip=True) if org.select_one('div._y10azs') else ""
                reviews_count = org.select_one('div._jspzdm').get_text(strip=True) if org.select_one('div._jspzdm') else "0"
                reviews_count = re.sub(r'\D', '', reviews_count)  # Оставляем только цифры
                
                organizations.append({
                    'Название': name,
                    'Категория': category,
                    'Рейтинг': rating,
                    'Кол-во отзывов': reviews_count,
                    'Ссылка': org.select_one('a._1rehek')['href'] if org.select_one('a._1rehek') else ""
                })
            except Exception as e:
                print(f"Ошибка парсинга организации: {e}")
                continue
        
        return organizations
    
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return []
    finally:
        driver.quit()

orgs_data = parse_building_organizations(url, max_orgs=1000)

# Сохранение в CSV
if orgs_data:
    df = pd.DataFrame(orgs_data)
    
    df.to_csv("2GIS_parsing\\organizations_data.csv", index=False, encoding='utf-8-sig')
else:
    print("Не удалось собрать данные об организациях")