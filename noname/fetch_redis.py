import requests
from itertools import chain
# from collections import namedtuple


class TopOptions(object):
    '''
    Just for autocomplete reasons, could be a dict
    '''
    def __init__(self, t='year', sort='top', limit=100, after=None):
        self.t = t
        self.sort = sort
        self.limit = limit
        self.after = after


USER_AGENT = 'noname version:1 url:https://github.com/papaloizouc/noname'
DEAFAULT_HEADERS = {
    'User-Agent': USER_AGENT
}

# some crazy staff
post_types = {'text', 'url', 'url_text'}
# optional_input = {'url': 2, 'selftext': 1, 'domain': 0}
# cast_post_type = {1: 'text', 2: 'url', 3: 'url_text'}


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


def get_subreddit_top_recursive(top_options, depth=1):
    '''
        :param top_options: Instance of TopOptions
        Just to avoid the recursion logic (if statements) in get_subreddit_top
        http://en.wikipedia.org/wiki/Separation_of_concerns
        could be generic recerse_function(f, *args, **kwargs)
    '''
    if depth <= 0:
        raise ValueError('Depth must be bigger than 0, given {}'.format(depth))

    posts = []
    for i in range(0, depth):
        #  TODO handle next arguement
        result = get_subreddit_top(top_options)
        posts.append(result)

    return chain(*posts)


def get_subreddit_top(top_options):
    '''
        :param top_options: Instance of TopOptions
        Calls http://www.reddit.com/dev/api#GET_{sort}
    '''
    response = requests.get(url='http://reddit.com/r/python/top.json',
                            headers=DEAFAULT_HEADERS,
                            params=vars(top_options))

    data = response.json()['data']
    children, after, before = data['children'], data['after'], data['before']
    posts = parse_posts(children)
    #  TODO return dict instead of list
    return posts

if __name__ == '__main__':
    get_subreddit_top()
