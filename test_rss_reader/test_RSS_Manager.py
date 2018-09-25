import unittest
from RSS_Manager.Source import RSS_URL_Management

class test_rss_reader(unittest.TestCase):
    def test_source(self):
        rssman = RSS_URL_Management()
        category = 'technology'
        testurl = r'https://www.wired.com/feed/category/ideas/latest/rss'
        rssman.addurl(category,testurl)

        self.assertEqual(rssman.urls[category][0],testurl)