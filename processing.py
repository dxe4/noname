from pprint import pprint
import nltk
from nltk import Text, word_tokenize, pos_tag
import redis
from collections import Counter

subreddit_info_keys = ['name', 'url']
subreddit_category_keys = ['top_week', 'hot', 'top_day', 'top_year', 'top_month']

class HasCodeException(Exception):
    """
        Comments with code add noise in text processing & statistics
        If any code is detected in comment this exception will be raised
    """
    pass

"""
ADJ	adjective	new, good, high, special, big, local
ADV	adverb	really, already, still, early, now
CNJ	conjunction	and, or, but, if, while, although
DET	determiner	the, a, some, most, every, no
EX	existential	there, there's
FW	foreign word	dolce, ersatz, esprit, quo, maitre
MOD	modal verb	will, can, would, may, must, should
N	noun	year, home, costs, time, education
NP	proper noun	Alison, Africa, April, Washington
NUM	number	twenty-four, fourth, 1991, 14:24
PRO	pronoun	he, their, her, its, my, I, us
P	preposition	on, of, at, with, by, into, under
TO	the word to	to
UH	interjection	ah, bang, ha, whee, hmpf, oops
V	verb	is, has, get, do, make, see, run
VD	past tense	said, took, told, made, asked
VG	present participle	making, going, playing, working
VN	past participle	given, taken, begun, sung
WH	wh determiner	who, which, when, what, where, how
"""

# ORIGIN: http://www.nltk.org/book/ch05.html#unsimplified-tags
def findtags(tag_prefix, tagged_text):
    cfd = nltk.ConditionalFreqDist((tag, word) for (word, tag) in tagged_text
                                  if tag.startswith(tag_prefix))
    return dict((tag, cfd[tag].keys()[:5]) for tag in cfd.conditions())


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

def extract_text(text):
    # print(text)
    tokens = word_tokenize(text)

    # Do we need to keep stopwords & len<2? not sure
    tokens = [i for i in tokens if not i in stopwords and len(i) > 2]
    counter = Counter(tokens)
    pprint(counter.most_common(10))

    tagged = pos_tag(tokens)
    # print(tagged)
    nouns = findtags('NN', tagged)
    pprint(nouns)

    verbs = findtags('V', tagged)
    pprint(verbs)
    ntlk_text = Text(tokens)
    print(text)

def process_comment(comment):
    body = comment["body"]
    score = comment["score"]

    if body.count("        ") >=2:
        raise HasCodeException
    if body:
        extract_text(body)
    # pprint(comment)

def process_post(post):
    comments = post["comments"]
    score = post["score"]
    text = post["text"]
    title = post["title"]
    url = post["url"]

    if text:
        pass
        # extract_text(text)
    else:
        print("no text ", url)
    comment_score_sum = sum([i["score"] for i in comments])
    print("score", score)
    print("comment_score_sum", comment_score_sum)
    print("\n\n")
    for comment in comments:
        try:
            process_comment(comment)
        except HasCodeException:
            pass  # Comment has code therefore adds noise in the statistics
    # pprint(post)

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

