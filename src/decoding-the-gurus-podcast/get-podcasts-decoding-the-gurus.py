import re
import requests
from pathlib import Path

from dateutil import parser
from bs4 import BeautifulSoup


def main():
    file_dir = Path(
        Path.home() / "git" / "podcasts" / "src" / "decoding-the-gurus-podcast"
    )
    file_dir.mkdir() if not file_dir.exists() else None

    existing_podcasts = list(Path.glob(file_dir, "*.mp3"))
    podcast_dates = [
        parser.parse(re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2}", p.name)[0]).date()
        for p in existing_podcasts
    ]

    feed_url = "https://feeds.captivate.fm/decoding-the-gurus/"
    content = BeautifulSoup(requests.get(feed_url).content)

    entries = content.find_all(name="item")

    titles = []
    mp3_links = []
    lengths = []
    pub_dates = []

    for item in entries:
        title = item.find(name="title").text.replace(" ", "-").replace(":-", "_")
        titles.append(title)

        link_candidate = item.find("enclosure")["url"]
        length_min = int(item.find("enclosure")["length"]) / 1e6
        lengths.append(length_min)

        pub_date = parser.parse(item.find(name="pubdate").text).date()
        pub_dates.append(pub_date)

        # Only download podcasts newer than the most recent podcast
        if pub_date > max(podcast_dates):

            file_name = f"{pub_date}-{title}.mp3"

            if link_candidate.endswith(".mp3"):
                print(f"Downloading: {title} ({pub_date})")
                mp3_links.append(link_candidate)

                with open(file_dir / file_name, "wb") as fout:
                    fout.write(requests.get(link_candidate).content)
            else:
                print(f"Unable to find link for {title}")


if __name__ == "__main__":
    main()
