from bs4 import BeautifulSoup, NavigableString, Tag
import requests

url = 'https://www.vlacem.ru/Arhiv/2025/res/5%20-%20Split%20_%2026042025.htm'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Получаем все группы (по <pre>)
pre_tags = soup.find_all('pre')

for group_index, pre in enumerate(pre_tags):
    print(f"\n📌 Группа #{group_index + 1}")
    children = list(pre.children)
    print(children)
    athletes = []
    current_athlete_data = []
    collecting = False  # флаг, что мы сейчас собираем сплиты

    for child in children:
        # Если встретили <u> — это начало нового блока
        if isinstance(child, Tag) and child.name == 'u':
            if collecting and current_athlete_data:
                # закончили собирать данные одного спортсмена
                athletes.append(current_athlete_data)
                current_athlete_data = []
            collecting = True
            continue

        # Если это текстовая строка или тег (например <b>)
        if collecting:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    current_athlete_data.append(text)
            elif isinstance(child, Tag) and child.name == 'b':
                # Текст внутри <b> — тоже часть строки
                bold_text = child.get_text(strip=True)
                if bold_text:
                    current_athlete_data.append(bold_text)

    # Добавляем последнего спортсмена (если был)
    if current_athlete_data:
        athletes.append(current_athlete_data)

    # Выводим результат
    for i, athlete_data in enumerate(athletes):
        # print(f"\n🏃 Спортсмен #{i+1}:")
        # Собираем сплиты как строки
        lines = ' '.join(athlete_data).split('\n')
        for line in lines:
            cleaned = line.strip()
            # if cleaned:
                # print(f"   {cleaned}")
