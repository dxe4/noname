import praw
import redis
from pprint import pprint
from collections import defaultdict
import time

subreddits_programming = {"python", "linux", "clojure", "haskell", "git", "programming", "opensource"}

info = {
    "hot": "get_hot",
    "top_day": "get_top_from_day",
    "top_month": "get_top_from_month",
    "top_week": "get_top_from_week",
    "top_year": "get_top_from_year",
}

def comment_info(comment):
    try:
        return {
            "body": comment.body,
            "score": comment.score,
        }
    except AttributeError:  # EVIL
        return {
            "body": None,
            "score": None
        }

def submission_info(submission):
    print("fetching submission {}".format(submission.title))

    time.sleep(0.5)  # Respect reddit for being awesome
    try:
        result = {
            "score": submission.score,
            "url": submission.url,
            "title": submission.title,
            "text": submission.selftext,
        }
        result["comments"] = [comment_info(i) for i in submission.comments]
        return result
    except AttributeError:  # EVIL v2
        return None


def fetch_info(s_reddit, func, limit):
    print("fetching info {}".format(func))
    submissions = getattr(s_reddit, func)(limit=limit)
    return [submission_info(i) for i in submissions]


def fetch_subreddit(redis_client, subreddit, limit=20):
    print("fetching sub reddit {}".format(subreddit))

    reddit = praw.Reddit(user_agent='seed_hack')
    s_reddit = reddit.get_subreddit(subreddit)

    result = {
        "url": s_reddit.url,
        "name": s_reddit.display_name
    }
    for k,v in info.items():
        result[k] = fetch_info(s_reddit, v, limit)

    pprint(result)
    redis_client.set(subreddit, result)

    print("done processing {}, waiting 5 seconds..".format(subreddit))
    time.sleep(5)


# bar()
redis_c = redis.StrictRedis(host='localhost', port=6379, db=0)
for subreddit in subreddits_programming:
    fetch_subreddit(redis_c, subreddit)
