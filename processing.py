from pprint import pprint
import nltk
from nltk import Text, word_tokenize, pos_tag
import redis
from collections import Counter
from urlparse import urlparse

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

class ExtractMixIn(object):
    def __init__(self, *args, **kwargs):
        self.most_common = None
        self.nouns = None
        self.verbs = None

    def extract_text(self, text):
        # print(text)
        tokens = word_tokenize(text)

        # Do we need to keep stopwords & len<2? not sure
        tokens = [i for i in tokens if not i in stopwords and len(i) > 2]
        counter = Counter(tokens)
        self.most_common = [i for i in counter.most_common(10) if i[1] > 1]

        tagged = pos_tag(tokens)
        self.nouns = findtags('NN', tagged)

        self.verbs = findtags('V', tagged)
        self.ntlk_text = Text(tokens)

    def to_dict(self):
        return {
            "common": self.most_common,
            "nouns": self.nouns,
            "verbs": self.verbs,
        }


class Comment(ExtractMixIn):
    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.body = kwargs["body"]
        self.score = kwargs["score"]

    def process(self):
        if self.body.count("        ") >= 2:
            raise HasCodeException
        if self.body:
            super(Comment, self).extract_text(self.body)

    def to_dict(self):
        _dict = super(Comment, self).to_dict()
        _dict.update({
            "body": self.body,
            "score": self.score,
        })
        return _dict


class Post(ExtractMixIn):
    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.comments = [Comment(**i) for i in kwargs["comments"]]
        self.score = kwargs["score"]
        self.text = kwargs["text"]
        self.title = kwargs["title"]
        self.url = kwargs["url"]
        self.comment_score_sum = sum([i.score for i in self.comments])
        self.url_only = False
        self.external_url = None
        if self.url:
            self.domain = urlparse(self.url).netloc

    def process(self):
        if self.text:
            super(Post, self).extract_text(self.text)
        else:
            self.url_only = True

        comments = []
        for comment in self.comments:
            try:
                comment.process()
                comments.append(comment)
            except HasCodeException:
                pass  # Comment has code therefore adds noise in the statistics
        # Remove comments that failed to be processed
        self.comments = comments

    def to_dict(self):
        _dict = super(Post, self).to_dict()
        _dict.update({
            "score": self.score,
            "text": self.text,
            "title": self.title,
            "url": self.url,
            "url_only": self.url_only,
            "comment_score_sum": self.comment_score_sum,
            "comments": [i.to_dict() for i in self.comments],
            "external_url": self.external_url,
            "domain": self.domain
        })
        return _dict


def get_sub_reddit_data(subreddit):
    """
        Fetch data from redis. dump exists in repo
    :param subreddit: subreddit to fetch. redis-cli, keys * shows all possible choices
    :return: subreddit dict
    """
    redis_c = redis.StrictRedis(host='localhost', port=6379, db=0)
    s_reddit = redis_c.get(subreddit)
    # print("EVIL "*1000) EVIL EVIL EVIL EVIL
    #  data is stored incorrectly no time to deal with it on a hackathon tho
    return eval(s_reddit)


def process_category(category):
    """
    :param category: one of this ['top_week', 'hot', 'top_day', 'top_year', 'top_month']
    """
    posts = []
    for post in category:
        post = Post(**post)
        post.process()
        posts.append(post)

    posts = sorted(posts, key=lambda x: -x.score)

    for i in posts:
        pprint(i.to_dict())


def process_subreddit(subreddit):
    data = get_sub_reddit_data(subreddit)
    name, url = data["name"], data["url"]
    for category in subreddit_category_keys:
        process_category(data[category])

if __name__ == "__main__":
    process_subreddit("python")

