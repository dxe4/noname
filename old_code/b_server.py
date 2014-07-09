from bottle import route, run, static_file, response
import redis

redis_c = redis.StrictRedis(host='localhost', port=6379, db=2)
def get_sub_reddit_data(subreddit):
    """
        Fetch data from redis. dump exists in repo
    :param subreddit: subreddit to fetch. redis-cli, keys * shows all possible choices
    :return: subreddit dict
    """
    s_reddit = redis_c.get(subreddit)
    # print("EVIL "*1000) EVIL EVIL EVIL EVIL
    # data is stored incorrectly no time to deal with it on a hackathon tho
    return eval(s_reddit)


@route('/hello')
def hello():
    return "Hello World!"

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/search/<section>/<word>')
def search(section, word):
    print(section)
    print(word)
    return {"data": get_sub_reddit_data(section)["neighbours"][word]}

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
