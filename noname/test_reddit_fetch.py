from copy import copy
import unittest
import noname

post = {
    'approved_by': None,
    'author': 'rya11111',
    'author_flair_css_class': None,
    'author_flair_text': None,
    'banned_by': None,
    'clicked': False,
    'created': 1387782629.0,
    'created_utc': 1387782629.0,
    'distinguished': None,
    'domain': 'reddit.com',
    'downs': 0,
    'edited': False,
    'gilded': 0,
    'hidden': False,
    'id': '1tilfi',
    'is_self': False,
    'likes': None,
    'link_flair_css_class': None,
    'link_flair_text': None,
    'media': None,
    'media_embed': {},
    'name': 't3_1tilfi',
    'num_comments': 27,
    'num_reports': None,
    'over_18': False,
    'permalink': '/r/Python/comments/1tilfi/congratulations_rpython_you_are_the_subreddit_of/',
    'saved': False,
    'score': 793,
    'secure_media': None,
    'secure_media_embed': {},
    'selftext': '',
    'selftext_html': None,
    'stickied': False,
    'subreddit': 'Python',
    'subreddit_id': 't5_2qh0y',
    'thumbnail': '',
    'title': 'Congratulations r/Python! You are the SUBREDDIT OF THE DAY!',
    'ups': 793,
    'url': 'http://www.reddit.com/r/subredditoftheday/comments/1tiler/december_23rd_2013_rpython_dont_worry_it_wont/',
    'visited': False
}


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.post = copy(post)
        self.parsed_post = noname.parse_post(self.post)

    def test_url_post(self):
        assert 'type' in self.parsed_post
        assert self.parsed_post['type'] == 'url'

if __name__ == '__main__':
    unittest.main()
