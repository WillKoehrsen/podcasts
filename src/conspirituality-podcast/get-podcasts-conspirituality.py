import requests
from pathlib import Path

from dateutil import parser
from bs4 import BeautifulSoup

from ..utils import HEADERS
from pathvalidate import sanitize_filename

FILE_DIR = Path(Path.home() / "Downloads" / "podcasts" / "conspirituality-podcast")
BASE_URL = "https://conspirituality.net/"


def process_content(content):
    articles = content.find_all("article")

    for article in articles:
        audio_link = article.find("audio").find("a").text
        title = article.find(attrs={"class": "podcast-meta-new-window"}).get("title")

        title = (
            (
                audio_link.split("/")[-1]
                if not title
                else "-".join(title.strip().split(" "))
            )
            .replace(":", "")
            .replace("w/", "")
        )

        pub_date = parser.parse(
            article.find("time", attrs={"class": "entry-date published"})["datetime"]
        ).date()

        file_name = sanitize_filename(f"{pub_date}-Ep-{title}.mp3")

        if (FILE_DIR / file_name).exists():
            continue

        with open(FILE_DIR / file_name, "wb") as fout:
            print(f"Downloading {file_name}")
            fout.write(requests.get(audio_link, headers=HEADERS).content)


def download_audio_from_pages():
    content = BeautifulSoup(requests.get(BASE_URL, headers=HEADERS).content)

    print("Processing base page...\n")
    process_content(content)

    not_found_text = "Page not found"

    for index in range(2, 20):
        print(f"\n\nProcessing page {index}\n")

        content = BeautifulSoup(
            requests.get(f"{BASE_URL}/page/{index}", headers=HEADERS).content
        )
        if content.title.text == not_found_text:
            break

        process_content(content)


if __name__ == "__main__":
    FILE_DIR.mkdir() if not FILE_DIR.exists() else None
    download_audio_from_pages()
