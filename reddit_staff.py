import praw
import redis
from pprint import pprint

info = {
    "hot": "get_hot",
    "top_day": "get_top_from_day",
    "top_month": "get_top_from_month",
    "top_week": "get_top_from_week",
    "top_year": "get_top_from_year",
}

def comment_info(comment):
    return {
        "body": comment.body,
        "score": comment.score,
    }

def submission_info(submission):
    return  {
        "score": submission.score,
        "url": submission.url,
        "title": submission.title,
        "text": submission.selftext,
        "comments": [comment_info(i) for i in submission.comments],
    }


def fetch_info(s_reddit, func, limit):
    submissions = list(getattr(s_reddit, func)(limit=limit))


def fetch_subreddit(subreddit, limit=20):
    reddit = praw.Reddit(user_agent='seed_hack')
    s_reddit = reddit.get_subreddit(subreddit)
    for k,v in info.items():
        fetch_info(s_reddit, v, limit)



def foo():

    a.get_top(),
    f = a.get_top_from_all(limit=10)
    print(list(f))

    raise Exception
    submissions = list(r.get_subreddit('opensource').get_hot(limit=5))

    print([str(x) for x in submissions])
    print([str(i) for i in submissions[0].comments])


    pprint(vars(submissions[0].comments[0]))

    # c.score, c.body

def bar():
    redis_c = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_c.set('foo', {"foo": "bar"})
    print(redis_c.get("foo"))

# bar()
fetch_subreddit("python")