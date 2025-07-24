import requests
from splits.masstart_winorient import MasStartWinOrient
from splits.relay_winorient import RelayWinOrient
from splits.splits_sportorg import SplitSportorg
from splits.splits_winorient import SplitsWinOrient


url1 = 'https://o-smolensk.ru/engine/download.php?id=3457'
url2 = 'https://www.vlacem.ru/Arhiv/2025/VS%20_%20Kovrov/res/3%20-%20Split%20_%2003062025.htm'
response = requests.get(url1)
response.encoding = 'utf-8'
splits = SplitsWinOrient(response.text)
keys = [x for x in splits.groups.keys()]
for key in keys:
    if not key.isalpha():
        response.encoding = 'windows-1251'
        splits = SplitsWinOrient(response.text)
        break
print(splits.groups.keys())