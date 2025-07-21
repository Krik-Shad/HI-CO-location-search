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

def parse_reviews(base_url, max_reviews=2000):
    try:
        driver.get(base_url)
        time.sleep(3)
        
        # Кликаем на вкладку "Отзывы" с повторными попытками
        for _ in range(3):
            try:
                reviews_tab = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a._2lcm958[href*="tab/reviews"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", reviews_tab)
                time.sleep(3)
                break
            except Exception as e:
                print(f"Попытка {_+1}: Не удалось найти вкладку 'Отзывы'")
                if _ == 2: return []
        
        # Находим панель прокрутки отзывов
        try:
            scroll_panel = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div._1rkbbi0x[data-scroll="true"]'))
            )
        except Exception as e:
            print(f"Не удалось найти панель отзывов: {e}")
            return []
        
        # Улучшенная система прокрутки с динамической загрузкой
        last_height = 0
        same_height_count = 0
        max_same_height = 5  # Максимум повторов без изменений
        loaded_reviews = set()
        
        while len(loaded_reviews) < max_reviews and same_height_count < max_same_height:
            # Получаем текущие отзывы перед прокруткой
            current_reviews = scroll_panel.find_elements(By.CSS_SELECTOR, 'div._1k5soqfl')
            
            # Прокручиваем вниз
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_panel)
            time.sleep(2)  # Важно дать время для загрузки
            
            # Проверяем новые отзывы
            new_reviews = scroll_panel.find_elements(By.CSS_SELECTOR, 'div._1k5soqfl')
            new_count = len(new_reviews)
            
            # Разворачиваем скрытые тексты
            try:
                more_buttons = scroll_panel.find_elements(By.CSS_SELECTOR, 'span._17ww69i')
                for btn in more_buttons:
                    try:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(0.1)
                    except:
                        continue
            except:
                pass
            
            # Проверяем прогресс
            if len(new_reviews) == len(current_reviews):
                same_height_count += 1
            else:
                same_height_count = 0
                print(f"Загружено отзывов: {len(new_reviews)}")
            
            # Защита от бесконечного цикла
            current_height = driver.execute_script("return arguments[0].scrollHeight", scroll_panel)
            if current_height == last_height:
                same_height_count += 1
            last_height = current_height
            
            # Если достигли конца
            try:
                end_marker = driver.find_element(By.CSS_SELECTOR, 'div._1q8q8s9, div._1h3cgic')  # Маркеры конца
                print("Достигнут конец списка отзывов")
                break
            except:
                pass
        
        # Собираем все уникальные отзывы
        reviews_html = scroll_panel.get_attribute('innerHTML')
        soup = BeautifulSoup(reviews_html, 'html.parser')
        reviews_data = []
        
        for review in soup.select('div._1k5soqfl'):
            try:
                author = review.select_one('span._16s5yj36').get_text(strip=True) if review.select_one('span._16s5yj36') else "Аноним"
                date = review.select_one('div._a5f6uz').get_text(strip=True) if review.select_one('div._a5f6uz') else ""
                
                text_element = review.select_one('a._1msln3t') or review.select_one('div._1msln3t')
                text = text_element.get_text(strip=True) if text_element else ""
                
                rating_container = review.select_one('div._1fkin5c')
                rating = len(rating_container.select('span')) if rating_container else 0
                
                reviews_data.append({
                    'Автор': author,
                    'Дата': date,
                    'Рейтинг': rating,
                    'Текст отзыва': text
                })
            except Exception as e:
                print(f"Ошибка парсинга отзыва: {e}")
                continue
        
        print(f"Всего собрано уникальных отзывов: {len(reviews_data)}")
        return reviews_data
    
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return []



reviews = parse_reviews(url, max_reviews=30)
# print(reviews)

if reviews:
    df = pd.DataFrame(reviews)
    df.to_csv("2GIS_parsing\\csv\\reviews_data.csv", index=False, encoding='utf-8-sig', sep=',')

else:
    print("Не удалось собрать отзывы")

driver.quit()