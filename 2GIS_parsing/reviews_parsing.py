import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from url_parsing import url
import pandas as pd


# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Открываем на весь экран
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Инициализация драйвера
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def parse_reviews(base_url, max_reviews=50):
    try:
        # Открываем страницу компании
        driver.get(base_url)
        time.sleep(3)
        
        # Кликаем на вкладку "Отзывы"
        try:
            reviews_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a._2lcm958[href*="tab/reviews"]'))
            )
            reviews_tab.click()
            time.sleep(3)
        except Exception as e:
            print(f"Не удалось найти вкладку 'Отзывы': {e}")
            return []
        
        # Прокрутка и загрузка отзывов
        last_height = driver.execute_script("return document.body.scrollHeight")
        loaded_reviews = 0
        
        while loaded_reviews < max_reviews:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Проверка новых отзывов
            reviews = driver.find_elements(By.CSS_SELECTOR, 'div._1k5soqfl')
            if len(reviews) > loaded_reviews:
                loaded_reviews = len(reviews)
            else:
                break  # Если новые отзывы не загружаются
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        try:
            read_more_buttons = driver.find_elements(By.CSS_SELECTOR, 'span._17ww69i')
            for button in read_more_buttons:
                try:
                    button.click()
                    time.sleep(0.5)
                except:
                    continue
        except:
            pass

        # Парсинг отзывов
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reviews_data = []
        
        for review in soup.select('div._1k5soqfl'):
            try:
                author = review.select_one('span._16s5yj36').get_text(strip=True)
                date = review.select_one('div._a5f6uz').get_text(strip=True)
                text = review.select_one('a._1msln3t').get_text(strip=True)
                rating_container = review.select_one('div._1fkin5c')
                if rating_container:
                    rating = len(rating_container.select('span'))
                else:
                    rating = 0
                
                reviews_data.append({
                    'Автор': author,
                    'Дата': date,
                    'Рейтинг': rating,
                    'Текст отзыва': text
                })
            except Exception as e:
                print(f"Ошибка парсинга отзыва: {e}")
        
        return reviews_data
    
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return []

reviews = parse_reviews(url, max_reviews=30)
# print(reviews)

if reviews:
    df = pd.DataFrame(reviews)
    df.to_csv("2GIS_parsing\\reviews_data.csv", index=False, encoding='utf-8-sig', sep=',')

else:
    print("Не удалось собрать отзывы")

driver.quit()