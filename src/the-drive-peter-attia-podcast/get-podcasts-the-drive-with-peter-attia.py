# import time
# from datetime import datetime
# from pathlib import Path

import requests
from bs4 import BeautifulSoup

# from rich.progress import track
from src.utils import HEADERS

POD_URL = "https://peterattiamd.com/podcast/archive/"


result = requests.get(POD_URL, headers=HEADERS)
soup = BeautifulSoup(result.content)

list_items = soup.find_all("li", {"class": "listing-item"})
list_item = list_items[0]

list_item_soup = BeautifulSoup(
    requests.get(list_item.find("a")["href"], headers=HEADERS).content
)

list_item_soup.find_all(
    "a", {"class": "spp-button-download spp-control spp-no-outline"}
)
