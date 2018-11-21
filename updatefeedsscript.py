from database import DatabaseManagement
from RSS_Manager import Feeds

links = DatabaseManagement.linksmanagement()
alllinks = links.getlinks()

for link_content in alllinks:
    link = link_content['link']
    category = link_content['category']
    fd = Feeds.feed(link,category=category)
    fdman = DatabaseManagement.feedsmanagement()
    fdman.addfeed(fd.content)





