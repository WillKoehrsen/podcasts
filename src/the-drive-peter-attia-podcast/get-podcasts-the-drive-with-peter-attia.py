import time
import requests
from pathlib import Path

from datetime import datetime

from bs4 import BeautifulSoup
from rich.progress import track

POD_URL = "https://peterattiamd.com/podcast/archive/"
from src.utils import HEADERS

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
