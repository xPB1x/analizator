import requests
from splits.sfr_splits import SFRSplits
from splits.sfr_masstart import SFRMasStart


url1 = 'https://o-site.spb.ru/_races/241117/241117_split.htm'
url2 = 'http://fso.karelia.ru/wp-content/uploads/2025/07/20250723_ResultList_ызд.htm'
response = requests.get(url1)
response.encoding = 'utf-8'
splits = SFRMasStart(response.text)
key = [x for x in splits.groups.keys()][0]
if not key[0].isalpha():
    response.encoding = 'windows-1251'
    splits = SFRMasStart(response.text)

print(splits.make_person_report('М21', 'МАКСИМЕНКО МИХАИЛ'))