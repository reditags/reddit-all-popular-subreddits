import math
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Set

import requests


class HotSubs:
    hot_subreddits: Set[str]

    subreddit_name: str
    post_count: int
    session: requests.Session

    def __init__(self, subreddit, post_count):
        self.hot_subreddits = set()

        self.subreddit_name = subreddit
        self.post_count = math.ceil(post_count / 100) * 100

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "reddit-all-popular-subreddits"})

        after = None
        retries = 0
        for i in range(int(self.post_count / 100)):
            print(f"{self}: downloading posts {i * 100:4} to {(i + 1) * 100:4}")
            if i != 0: sleep(1)
            r = self.session.get(
                f"https://reddit.com/r/{self.subreddit_name}.json",
                params={"after": after, "limit": 100},
            )
            if r.status_code == 503:
                    import time
                    time.sleep(60)
                    continue
            elif r.status_code != 200:
                retries += 1
                if retries > 10:
                    print(r.status_code)
                    print(r.text)
                    print("too many retries")
                    exit(1)
                i -= 1
                self.session = requests.Session()
                self.session.headers.update({"User-Agent": "reddit-all-popular-subreddits"})
                print("retrying with new session")
                continue
            else:
                retries = 0
            data = r.json()["data"]
            after = data["after"]

            for post in data["children"]:
                self.hot_subreddits.add(post["data"]["subreddit"])

        print(f"{self}: ready with subs from {self.post_count} posts")

    def __repr__(self):
        return f"HotSubs /r/{self.subreddit_name}"

    def __iter__(self):
        return sorted(self.hot_subreddits, key=str.lower).__iter__()


def update(post_count=6969):
    subreddits = set()

    Path("data/").mkdir(exist_ok=True)
    timestamp = datetime.today().strftime("%Y-%m")
    save_file = Path(f"data/{timestamp}.txt")
    if save_file.exists():
        subreddits.update(save_file.read_text().splitlines())
        print(f"loaded {len(subreddits)} hot subs from {save_file}")

    subreddits.update(HotSubs("all", post_count))
    subreddits.update(HotSubs("popular", post_count))

    save_file.write_text("\n".join(sorted(subreddits, key=str.lower)))
    print(f"saved {len(subreddits)} /r/all, /r/popular hot subs to {save_file}")


if __name__ == "__main__":
    update()
