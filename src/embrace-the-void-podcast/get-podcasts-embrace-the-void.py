import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rich.progress import track

POD_URL = "https://voidpod.com/podcasts"


def process_url(url):
    response = requests.get(url)

    # Wait if encounter too many requests
    while response.status_code != 200:
        print(f"{response.status_code} encountered with page: {url}")
        time.sleep(15)
        response = requests.get(url)

    content = BeautifulSoup(requests.get(url).content)
    posts = content.find_all(attrs={"data-layout-label": "Post Body"})
    older_link_ext = content.find(attrs={"class": "older"}).get("href")

    return dict(
        posts=[process_post(post) for post in posts], older_link_ext=older_link_ext
    )


def process_post(post):
    pub_date = datetime.fromtimestamp(float(post["data-updated-on"]) / 1000).date()
    post_title = post.find(attrs={"class": "sqs-audio-embed"})["data-title"]
    mp3_url = post.find(attrs={"class": "sqs-audio-embed"})["data-url"]

    return pub_date, post_title, mp3_url


def next_page_from_older_ext(older_link_ext):
    return f"{POD_URL}?{older_link_ext.split('?')[-1]}"


def download_file(pub_date, raw_title, download_link):
    title = f"{pub_date}-{raw_title.replace('- ', '').replace(' ', '_')}"

    if download_link.endswith(".mp3"):
        download_file_name = FILE_DIR / f"{title}.mp3"

        if download_file_name.exists():
            print(f"Found existing file, skipping: {title}")

        else:
            print(f"Downloading: {title} ({pub_date})")
            with open(download_file_name, "wb") as fout:
                fout.write(requests.get(download_link).content)


if __name__ == "__main__":
    FILE_DIR = Path(Path.home() / "Downloads" / "podcasts" / "embrace-the-void-podcast")
    FILE_DIR.mkdir() if not FILE_DIR.exists() else None

    existing_podcasts = list(Path.glob(FILE_DIR, "*mp3"))

    print(f"Found existing podcasts: {existing_podcasts}")

    # Process the first page
    page_results = process_url(POD_URL)
    posts_info = page_results["posts"]
    older_link_ext = page_results["older_link_ext"]

    next_page_url = next_page_from_older_ext(older_link_ext)

    # Continue until there is a page with no further older url
    while next_page_url:

        page_results = process_url(next_page_url)
        posts_info.extend(page_results["posts"])
        older_link_ext = page_results.get("older_link_ext")

        next_page_url = (
            next_page_from_older_ext(older_link_ext) if older_link_ext else None
        )

    print(f"Found {len(posts_info)} podcasts.")

    for (pub_date, raw_title, download_link) in track(posts_info):
        download_file(pub_date, raw_title, download_link)
