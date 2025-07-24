import requests
from splits.masstart_winorient import MasStartWinOrient
from splits.relay_winorient import RelayWinOrient
from splits.splits_sportorg import SplitSportorg
from splits.splits_winorient import SplitsWinOrient


url1 = 'https://pr2025.fsono.ru/wp-content/uploads/2025/05/3-Split-_-04052025.htm'
url2 = 'https://www.vlacem.ru/Arhiv/2025/VS%20_%20Kovrov/res/3%20-%20Split%20_%2003062025.htm'
response = requests.get(url1)
response.encoding = 'utf-8'
splits = SplitsWinOrient(response.text)
key = [x for x in splits.groups.keys()][0]
key = key[0]
if not key.isalpha():
    response.encoding = 'windows-1251'
    splits = SplitsWinOrient(response.text)

print(splits.get_top10_on_leg('Start -> 31'))