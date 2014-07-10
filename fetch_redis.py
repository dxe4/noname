import requests

USER_AGENT = "noname version:1 url:https://github.com/papaloizouc/noname"
headers = {
    "User-Agent": USER_AGENT
}


def get_subreddit():
    params = {
        "t": "year",
        "sort": "top",
    }
    x = requests.get(url="http://reddit.com/r/python/top.json",
                 headers=headers,
                 params=params)
    from pprint import pprint
    resp = x.json()["data"]
    children, after, before = resp["children"], resp["after"], resp["before"]
    pprint(children)


if __name__ == "__main__":
    get_subreddit()
