from database import DatabaseManagement
from RSS_Manager import Processing
from RSS_Manager import Feeds
import time

feeds = DatabaseManagement.feedsmanagement()
client = feeds.database.client

for doc in client.rssdata.rssentries.find({'urltextsummary':{'$exists':False}}):
    link = doc['link']
    rssnltk = Processing.RSSNLTK()
    sitetext = rssnltk.getHTMLtext(link)
    summarysentences = rssnltk.scoresentences(sitetext)
    summarysentences = sorted(summarysentences, key=rssnltk.filtercount,reverse=True)
    top3summarysentences = [x['sentence'] for x in summarysentences[0:3]]
    top3scores = [x['score'] for x in summarysentences[0:3]]
    status = client.rssdata.rssentries.update({
        'id': doc['id'],
        'author': doc['author'],
        'title': doc['title']},
       {'$set':{'urltext':sitetext,
                'urltextsummary':top3summarysentences,
                'urltextsummaryscore':top3scores}},
       True)

f = open(r"/home/apluser/PycharmProjects/rss_reader/status.txt", "a")
f.write(time.strftime("update urls: %D %T\n"))
f.close()