from selenium import webdriver
from splits.splits_sportorg import SplitSportorg
from splits.masstart_sportorg import MasStartSportorg
import time
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument('--headless')
with webdriver.Chrome(options=options) as browser:
    browser.get('https://www.vlacem.ru/Arhiv/2022/res/21%20-%20Split%20_%2023102022.html?sportorg=1')
    browser.find_element(By.CSS_SELECTOR, 'div.sportorg-settings-row > button').click()
    lables = browser.find_elements(By.CSS_SELECTOR, 'div.sportorg-settings-row')
    for lable in lables:
        if lable.text == 'Сплиты (все отметки)':
            lable.click()
            break
    print('eee')

    html = browser.page_source
    splits = MasStartSportorg(html)
    print(splits.make_person_report('МУЖЧИНЫ', 'Брызгалов Павел'))