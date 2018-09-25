from unittest import TestCase
from unittest import mock
import feedparser
import RSS_Manager.Feeds as feedman
import time
class TestFeed(TestCase):
    def test_getfeed(self):
        feed = feedman.feed(r'https://www.wired.com/feed/category/ideas/latest/rss','technology')
        feed.getfeed()
        res = feed.getvalue('entries')
        self.assertIsNotNone(res)

    def test_gettag(self):
        feed = feedman.feed(r'https://www.wired.com/feed/category/ideas/latest/rss','technology')
        self.assertEqual(feed.url,r'https://www.wired.com/feed/category/ideas/latest/rss')
