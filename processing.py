from pprint import pprint
from nltk import Text, word_tokenize
import redis

subreddit_info_keys = ['name', 'url']
subreddit_category_keys = ['top_week', 'hot', 'top_day', 'top_year', 'top_month']

def get_stopwords():
    lines = []
    with open("stopwords") as f:
        lines = [i.strip() for i in f.readlines()]
    return lines

stopwords = get_stopwords()


def get_sub_reddit_data(subreddit):

    """
        Fetch data from redis. dump exists in repo
    :param subreddit: subreddit to fetch. redis-cli, keys * shows all possible choices
    :return: subreddit dict
    """
    redis_c = redis.StrictRedis(host='localhost', port=6379, db=0)
    s_reddit = redis_c.get(subreddit)
    #  print("EVIL "*1000) EVIL EVIL EVIL EVIL
    #  data is stored incorrectly no time to deal with it on a hackathon tho
    return eval(s_reddit)

def process_comment(comment):
    body = comment["body"]
    score = comment["score"]
    pprint(comment)

def process_post(post):
    comments = post["comments"]
    score = post["score"]
    score = post["text"]
    score = post["title"]
    url = post["url"]

    for comment in comments:
        process_comment(comment)
    pprint(post)

def process_category(category):
    """
    :param category: one of this ['top_week', 'hot', 'top_day', 'top_year', 'top_month']
    """
    for post in category:
        process_post(post)

def process_subreddit(subreddit):
    data = get_sub_reddit_data(subreddit)
    name, url = data["name"], data["url"]
    for category in subreddit_category_keys:
        process_category(data[category])


process_subreddit("python")

