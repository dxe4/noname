import requests

USER_AGENT = 'noname version:1 url:https://github.com/papaloizouc/noname'
headers = {
    'User-Agent': USER_AGENT
}

# some crazy staff
post_types = {'text', 'url', 'url_text'}
optional_input = {'url': 2, 'selftext': 1, 'domain': 0}
cast_post_type = {1: 'text', 2: 'url', 3: 'url_text'}


def _determine_type(domain, text):

    if domain == "self.Python":
        return "text"
    elif text:
        return "text_url"
    else:
        return "url"

def parse_post(post_dict):
    # Required Fields
    domain = post_dict["domain"]
    text = post_dict.get("selftext")
    post_type = _determine_type(domain, text)
    return {
        'score': post_dict['score'],
        'title': post_dict['title'],
        'name': post_dict['name'],
        'url': post_dict['url'],
        'domain': domain ,
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
    x = requests.get(url='http://reddit.com/r/python/top.json',
                     headers=headers,
                     params=params)
    from pprint import pprint

    resp = x.json()['data']
    children, after, before = resp['children'], resp['after'], resp['before']
    pprint(children)
    print(after)
    print(before)
    for child in children:
        data = child['data']
        post = parse_post(data)
        pprint(post)



if __name__ == '__main__':
    get_subreddit()
