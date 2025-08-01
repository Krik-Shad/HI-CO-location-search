import pandas as pd

# Загружаем оба CSV файла
df1 = pd.read_csv('2GIS_parsing\\csv\\reviews_data.csv')
df2 = pd.read_csv('2GIS_parsing\\static_data.csv')
df3 = pd.read_csv('2GIS_parsing\\csv\\organizations_data.csv')

# Объединяем один под другим
combined_df = pd.concat([df1, df2, df3], ignore_index=True)

# Сохраняем результат
combined_df.to_csv('2GIS_parsing\\csv\\combined_data.csv', index=False, encoding='utf-8-sig')