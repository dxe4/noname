import requests
from pprint import pprint

USER_AGENT = 'noname version:1 url:https://github.com/papaloizouc/noname'
DEAFAULT_HEADERS = {
    'User-Agent': USER_AGENT
}

# some crazy staff
post_types = {'text', 'url', 'url_text'}
optional_input = {'url': 2, 'selftext': 1, 'domain': 0}
cast_post_type = {1: 'text', 2: 'url', 3: 'url_text'}


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


def get_subreddit():
    params = {
        't': 'year',
        'sort': 'top',
        'limit': 100
    }
    # params['after']= 't3_1qpbwi'
    response = requests.get(url='http://reddit.com/r/python/top.json',
                            headers=DEAFAULT_HEADERS,
                            params=params)

    data = response.json()['data']
    children, after, before = data['children'], data['after'], data['before']
    pprint(children)
    for child in children:
        child_data = child['data']
        post = parse_post(child_data)
        pprint(post)


if __name__ == '__main__':
    get_subreddit()
