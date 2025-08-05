from selenium import webdriver
from splits.splits_sportorg import SplitSportorg
from splits.set_direction_sportorg import SplitsSportorgDirection
import time
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument('--headless')
with webdriver.Chrome(options=options) as browser:
    browser.get('https://ros2025.ul-orient.ru/wp-content/uploads/2025/08/20250801_протокол_результатов_сплиты.html?sportorg=1')

    browser.find_element(By.CSS_SELECTOR, 'div.sportorg-settings-row > button').click()
    labels = browser.find_elements(By.CSS_SELECTOR, 'div.sportorg-settings-row')
    for label in labels:
        if label.text.strip() == 'Сплиты (все отметки)':
            label.click()
    html = browser.page_source
    splits = SplitSportorg(html)
    print(splits.get_top10_on_each_leg_group('М50'))