from pprint import pprint
import nltk
from nltk import Text, word_tokenize, pos_tag
import redis
from collections import Counter
from urlparse import urlparse
from collections import defaultdict
import re

subreddit_info_keys = ['name', 'url']
subreddit_category_keys = ['top_week', 'hot', 'top_day', 'top_year', 'top_month']

subreddits_programming = ["java", "javascript", "nodejs", "php", "linux", "mac", "iphone", "android", "google",
                          "microsoft", "python", "linux", "clojure", "haskell", "git", "programming", "opensource"]

# save the processed data in another db (1)
redis_c = redis.StrictRedis(host='localhost', port=6379, db=1)


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


def find_neighboors(tokens, word):
    neighbours = []
    for count, token in enumerate(tokens):
        if word == token:
            try:
                neighbours.append((tokens[count - 1], tokens[count + 1]))
            except IndexError:
                pass
    return neighbours


class ExtractMixIn(object):
    def __init__(self, *args, **kwargs):
        self.most_common_repeated = None
        self.nouns = None
        self.verbs = None

    def clean_text(self, text):
        return re.sub('[^a-zA-Z0-9]', ' ', text)

    def extract_text(self, text):
        text = self.clean_text(text)
        tokens = word_tokenize(text)
        # Do we need to keep stopwords & len<2? not sure
        tokens = [i.lower() for i in tokens if not i.lower() in stopwords and len(i) > 3]
        self.tokens = tokens  # kind of a hack
        counter = Counter(tokens)
        most_common_repeated = [i for i in counter.most_common(50) if i[1] > 1]

        tagged = pos_tag(tokens)
        nouns = findtags('NN', tagged)

        verbs = findtags('V', tagged)
        # self.ntlk_text = Text(tokens)

        return most_common_repeated, nouns, verbs, counter


class Details(object):
    def __init__(self, most_common_repeated, nouns, verbs, counter):
        self.most_common_repeated = most_common_repeated
        self.nouns = nouns,
        self.verbs = verbs
        self.counter = counter

    def to_dict(self):
        return {
            "most_common_repeated": self.most_common_repeated,
            "nouns": self.nouns,
            "verbs": self.verbs,
            "counter": self.counter,
        }


class Comment(ExtractMixIn):
    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.body = kwargs["body"]
        self.score = kwargs["score"]

    def process(self):
        if self.body is not None and self.body.count("        ") >= 2:
            raise HasCodeException
        if self.body:
            self.details = Details(*super(Comment, self).extract_text(self.body))

    def to_dict(self):
        try:
            return {
                "body": self.body,
                "score": self.score,
                "details": self.details.to_dict(),
                "tokens": self.tokens,
            }
        except AttributeError:
            return {
                "body": None,
                "score": None,
                "details": None,
            }


class Post(ExtractMixIn):
    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.comments = [Comment(**i) for i in kwargs["comments"]]
        self.score = kwargs["score"]
        self.text = kwargs["text"]
        self.title = kwargs["title"]
        self.url = kwargs["url"]
        self.comment_score_sum = sum([i.score for i in self.comments if i.score is not None])
        self.url_only = False
        self.external_url = None
        self.domain = urlparse(self.url).netloc
        self.title_statistics = None
        self.text_statistics = None
        if self.domain != "www.reddit.com":
            self.external_url = self.domain
        if self.text:
            self.text_statistics = Details(*self.extract_text(self.text))
        if self.title:
            self.title_statistics = Details(*self.extract_text(self.title))

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
        _dict = {
            "score": self.score,
            "text": self.text,
            "title": self.title,
            "url": self.url,
            "url_only": self.url_only,
            "comment_score_sum": self.comment_score_sum,
            "comments": [i.to_dict() for i in self.comments],
            "external_url": self.external_url,
            "domain": self.domain,
            "tokens": self.tokens,
        }
        if self.title_statistics:
            _dict["title_statistics"] = self.title_statistics.to_dict()

        if self.text_statistics:
            _dict["text_statistics"] = self.text_statistics.to_dict()
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
    # data is stored incorrectly no time to deal with it on a hackathon tho
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

    result = [i.to_dict() for i in posts]
    return result


def process_subreddit(subreddit):
    data = get_sub_reddit_data(subreddit)
    name, url = data["name"], data["url"]
    result = []
    for category in subreddit_category_keys:
        if category == "hot":  # skip hot for now because its unique
            continue
        posts = process_category(data[category])
        for i in posts:
            result.append(i)
    result = sorted(result, key=lambda x: -x["score"])
    return result


def process_statistics(statistics, all_words, result, type):
    try:
        title_s = result[type]
        if title_s is None:
            return statistics, all_words
        for word in title_s["most_common_repeated"]:
            statistics["most_common_repeated"][word[0]] += word[1]
        for k, v in title_s["verbs"].items():
            for word in v:
                statistics["verbs"][word] += 1
        for k, v in title_s["nouns"][0].items():
            for word in v:
                statistics["nouns"][word] += 1
    except KeyError as e:
        if type == "text_statistics":
            statistics["other"][result["external_url"]] += 1
    try:
        for k, v in result[type]["counter"].items():
            all_words["all"][k] += v
    except KeyError:
        pass  # EVIL v10
    return statistics, all_words


def safe_del_key(_dict, key):
    try:
        del _dict[key]
    except KeyError:
        pass


def statistics_object():
    return {
        "most_common_repeated": defaultdict(int),
        "verbs": defaultdict(int),
        "nouns": defaultdict(int),
        "other": defaultdict(int),
        "all": defaultdict(int),
    }


def statistics_objects():
    return [statistics_object() for i in range(0, 4)]


min_count = {
    0: 2,
    1: 2,
    2: 12,
    3: 20,
}


def spam_eggs_bad_name(sub_reddit):
    result = process_subreddit(sub_reddit)
    # pprint(result)
    all_statistics = statistics_objects()
    title_statistics, text_statistics, comments_statistics, all_words = all_statistics

    for i in result:
        text_statistics, all_words = process_statistics(
            text_statistics, all_words, i, "text_statistics")

        title_statistics, all_words = process_statistics(
            title_statistics, all_words, i, "title_statistics")

        for comment in i["comments"]:
            comments_statistics, all_words = process_statistics(
                comments_statistics, all_words, comment, "details")


    neighbours = defaultdict(list)
    to_save = {}
    for count, statistics in enumerate(all_statistics):
        for k, v in statistics.items():
            # https/http must have been captured from urls?
            print(k)
            final_result = {a: b for a, b in v.items() if b > min_count[count]
                    if not a in ("http", "https")}

            if count == 3:
                to_save = final_result
                for word in final_result :
                    for i in result:
                        neighbours_found = find_neighboors(i["tokens"], word)
                        neighbours[word].extend(neighbours_found)
                        for j in i["comments"]:
                            try:
                                neighbours_found = find_neighboors(j["tokens"], word)
                                neighbours[word].extend(neighbours_found)
                            except KeyError:
                                pass

    redis_c.set(sub_reddit, {
        "most_popular": to_save,
        "neighbours": dict(neighbours),
    })


if __name__ == "__main__":
    for i in subreddits_programming:
        spam_eggs_bad_name(i)
