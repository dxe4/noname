from copy import deepcopy
import requests
# from itertools import chain
# from collections import namedtuple


USER_AGENT = 'noname version:1 url:https://github.com/papaloizouc/noname'
DEAFAULT_HEADERS = {
    'User-Agent': USER_AGENT
}


class FetchError(Exception):
    '''
        Raised when a subreddit could not be fetched (status_code != 200)
    '''
    pass


class TopOptions(object):

    '''
    Just for autocomplete reasons, could be a dict
    '''

    def __init__(self, t='year', sort='top', limit=100, after=None,
                 before=None):
        self.t = t
        self.sort = sort
        self.limit = limit
        self.after = after
        self.before = before


def _determine_type(domain, text):
    '''
    :returns: one of [text, text_url, url]
    text: Not an external link
    text_url: External link with text in the post
    url: External Link without text in the post
    '''
    if domain == "self.Python":
        return "text"
    elif text:
        return "text_url"
    else:
        return "url"


def parse_post(post_dict):
    '''
    :param post_dict: dictionary as returned by reddis api
    :returns: dict with keys: score, title, name, url, domain, created_utc, type
    '''
    # Required Fields
    domain = post_dict["domain"]
    text = post_dict.get("selftext")
    post_type = _determine_type(domain, text)

    return {
        'score': post_dict['score'],
        'title': post_dict['title'],
        'name': post_dict['name'],
        'url': post_dict['url'],
        'domain': domain,
        'created_utc': post_dict['created_utc'],
        "type": post_type
    }


def parse_posts(children):
    '''
    :param children: Dict as given by response.json()['data']['children]
    '''
    return [parse_post(child['data'])
            for child in children]


def get_subreddit_top_recursive(subreddit, top_options=None, depth=1):
    '''
        :param top_options: Instance of TopOptions
        Just to avoid the recursion logic (if statements) in get_subreddit_top
        http://en.wikipedia.org/wiki/Separation_of_concerns
        could be generic recerse_function(f, *args, **kwargs)
        Raises FetchError if resonse.status_code != 200
        Raises ValueError if depth <= 0
    '''
    if depth <= 0:
        raise ValueError('Depth must be bigger than 0, given {}'.format(depth))

    if top_options is None:
        top_options = TopOptions()

    posts = []
    for i in range(0, depth):
        result = get_subreddit_top(subreddit, top_options=top_options)

        #  Next posts fetched will start after this posts last
        top_options = deepcopy(top_options)
        top_options.after = result['after']

        posts.append(result)

    return posts


def get_subreddit_top(subreddit, top_options=None):
    '''
        :param top_options: Instance of TopOptions
        Calls http://www.reddit.com/dev/api#GET_{sort}
        Raises FetchError if resonse.status_code != 200
    '''
    if top_options is None:
        top_options = TopOptions()

    url = 'http://reddit.com/r/{}/top.json'.format(subreddit)
    response = requests.get(url=url,
                            headers=DEAFAULT_HEADERS,
                            params=vars(top_options))

    if response.status_code != 200:
        raise FetchError("Couldn't fetch subreddit {}. status_code: {}".format(
            subreddit, response.status_code))

    data = response.json()['data']
    children, after, before = data['children'], data['after'], data['before']
    posts = parse_posts(children)

    result = {
        'posts': posts,
        'after': after,
        'before': before,
    }
    return result

if __name__ == '__main__':
    res = get_subreddit_top_recursive('python', depth=2)
