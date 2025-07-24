import requests
from splits.sfr_splits import SFRSplits


url1 = 'https://www.vlacem.ru/Arhiv/2025/res/4%20-%20Split%20_%2020042025.htm#МЭлита'
url2 = 'http://fso.karelia.ru/wp-content/uploads/2025/07/20250723_ResultList_ызд.htm'
response = requests.get(url2)
response.encoding = 'utf-8'
splits = SFRSplits(response.text)
key = [x for x in splits.groups.keys()][0]
if not key[0].isalpha():
    response.encoding = 'windows-1251'
    splits = SFRSplits(response.text)

print(splits.get_top10_on_each_leg_group('М21'))