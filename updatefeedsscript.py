from database import DatabaseManagement
from RSS_Manager import Feeds
import time


links = DatabaseManagement.linksmanagement()
alllinks = links.getlinks()

for link_content in alllinks:
    link = link_content['link']
    category = link_content['category']
    fd = Feeds.feed(link,category=category)
    fdman = DatabaseManagement.feedsmanagement()
    fdman.addfeed(fd.content)

f = open(r"/home/apluser/PycharmProjects/rss_reader/status.txt", "a")
f.write(time.strftime("update Feeds: %D %T\n"))
f.close()