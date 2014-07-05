import nltk
from nltk import Text, word_tokenize
import redis
redis_c = redis.StrictRedis(host='localhost', port=6379, db=0)

print(Text)

def get_stopwords():
    lines = []
    with open("stopwords") as f:
        lines = [i.strip() for i in f.readlines()]
    return lines

stopwords = get_stopwords()

