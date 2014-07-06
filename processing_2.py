"""
tHIS CODE IS FULL OF BAD PRACTICES DON'T GET INSPIRED BY IT...
the processing.py ended up being a complete mess.
this file will process what processing.py pushed in redis
"""

import redis
from pprint import pprint

subreddits_programming = ["java", "javascript", "nodejs", "php", "linux", "mac", "iphone", "android", "google",
                          "microsoft", "python", "linux", "clojure", "haskell", "git", "programming", "opensource"]


redis_c = redis.StrictRedis(host='localhost', port=6379, db=1)

def get_sub_reddit_data(redis_c, subreddit):
    """
        Fetch data from redis. dump exists in repo
    :param subreddit: subreddit to fetch. redis-cli, keys * shows all possible choices
    :return: subreddit dict
    """
    s_reddit = redis_c.get(subreddit)
    # print("EVIL "*1000) EVIL EVIL EVIL EVIL
    # data is stored incorrectly no time to deal with it on a hackathon tho
    return eval(s_reddit)

x = get_sub_reddit_data(redis_c, "java")
pprint(x)
