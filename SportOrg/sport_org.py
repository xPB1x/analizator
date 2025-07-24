from selenium import webdriver
from splits.splits_sportorg import SplitSportorg
from splits.masstart_sportorg import MasStartSportorg
import time
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument('--headless')
with webdriver.Chrome(options=options) as browser:
    browser.get('https://o-bash.ru/wp-content/uploads/2025/06/Splity-CHIP-PFO-29.06.2025.html?sportorg=1')
    browser.find_element(By.CSS_SELECTOR, 'div.sportorg-settings-row > button').click()
    lables = browser.find_elements(By.CSS_SELECTOR, 'div.sportorg-settings-row')
    for lable in lables:
        if lable.text == 'Сплиты (все отметки)':
            lable.click()
            break
    print('eee')

    html = browser.page_source
    splits = MasStartSportorg(html)
    print(splits.get_top10_on_each_leg_group('Мужчины'))