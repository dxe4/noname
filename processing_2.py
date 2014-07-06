"""
tHIS CODE IS FULL OF BAD PRACTICES DON'T GET INSPIRED BY IT...
the processing.py ended up being a complete mess.
this file will process what processing.py pushed in redis
"""

import redis
from pprint import pprint
import pygal

subreddits_programming = ["java", "javascript", "nodejs", "php", "linux", "mac", "iphone", "android", "google",
                          "microsoft", "python", "linux", "clojure", "haskell", "git", "programming", "opensource"]


redis_c = redis.StrictRedis(host='localhost', port=6379, db=2)

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

def make_svg(subreddit):
    xx = get_sub_reddit_data(redis_c, subreddit)

    data = sorted([(k,v) for k,v in xx["most_popular"].items()], key=lambda x: -x[1])[1:20]


    chart = pygal.HorizontalBar(rounded_bars=20, width=900, height=700,
                                explicit_size=True, legend_font_size=20,
                                tooltip_font_size=24, title=subreddit,
                                title_font_size=24)
    for k,v in data:
        chart .add(k, v)
    chart.render_to_file('{}.svg'.format(subreddit))

for i in subreddits_programming:
    make_svg(i)
