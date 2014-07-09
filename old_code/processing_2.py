"""
tHIS CODE IS FULL OF BAD PRACTICES DON'T GET INSPIRED BY IT...
the processing.py ended up being a complete mess.
this file will process what processing.py pushed in redis
"""
from collections import OrderedDict

import redis
from pprint import pprint
import pygal
from collections import defaultdict

subreddits_programming = ["java", "javascript", "nodejs", "php", "linux", "mac", "iphone", "android", "google",
                          "microsoft", "python", "clojure", "haskell", "git", "programming", "opensource"]


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


    chart = pygal.HorizontalBar(rounded_bars=20, width=700, height=700,
                                explicit_size=True, legend_font_size=18,
                                tooltip_font_size=24, title=subreddit,
                                title_font_size=24, spacing=20)
    for k,v in data:
        chart .add(k, v)
    chart.render_to_file('{}.svg'.format(subreddit))


def times_found(all_data, subreddit, item):
    times = 1
    for k, v in all_data.items():
        if k != subreddit:
            for i in v:
                if i[0] == item:
                    times+=1
    return times


def pick_common_word(all_data, word):
    result = set()
    for k,v in all_data.items():
        for i in v:
            if i[0] == word:
                result.add((k, i[1]))
    return result

def make_common_svg():
    """
        WHAT A MESS !!!!!!
    """
    all_data = {}
    for i in subreddits_programming:
        xx = get_sub_reddit_data(redis_c, i)
        data = sorted([(k,v) for k,v in xx["most_popular"].items()], key=lambda x: -x[1])[1:20]
        all_data[i] = data

    common = set()
    for k, v in all_data.items():
        new_set = {i[0] for i in v if times_found(all_data, k, i[0]) > 5}
        common = common.union(new_set)

    picked_common = []
    for i in common:
        picked_common.append([i,pick_common_word(all_data, i)])

    picked_common2 = defaultdict(list)
    for i in picked_common:
        processed_pairs = []
        for pair in i[1]:
            picked_common2[pair[0]].append(pair[1])
            processed_pairs.append(pair[0])
            if pair[0] == "linux":
                print("f", i[0])
        for zz in subreddits_programming:
            if not zz in processed_pairs:
                if zz == "linux":
                    print("s", i[0])
                picked_common2[zz].append(None)


    stackedbar_chart = pygal.StackedBar(width=1200, height=800,
                                explicit_size=True, legend_font_size=24,
                                tooltip_font_size=24, title="Common",
                                title_font_size=24, spacing=20)
    stackedbar_chart.title = 'Common words !'
    stackedbar_chart.x_labels = [i[0] for i in picked_common]


    for k,v in dict(picked_common2).items():
        stackedbar_chart.add(k,v)
    stackedbar_chart.render_to_file("common.svg")


if __name__ == "__main__":
    # for i in subreddits_programming:
        #make_svg(i)
    # make_common_svg()
    x = get_sub_reddit_data(redis_c, "python")
    pprint(x)
