import json
from bs4 import BeautifulSoup

html = open("mutual_fund_raw.html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, 'lxml')

next_data = soup.find('script', id='__NEXT_DATA__')
if next_data and next_data.string:
    data = json.loads(next_data.string)
    with open("next_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved __NEXT_DATA__ to next_data.json")
