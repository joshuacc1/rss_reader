import feedparser
import pprint

def getlinks():
    f = open(r'C:\Users\combsjc1\Documents\Python Scripts\rsslinks.txt')
    links = {}
    for line in f.readlines():
        lline = line.split(',')
        category = lline[0]
        link = lline[1]
        if not category in links:
            links[category] = []
            links[category].append(link)
        else:
            links[category].append(link)
    f.close()
    return links

def getrssfeeds(links, showfeeds = False):
    #links = getlinks()
    feeds = {}
    for category in links:
        for link in links[category]:
            d = feedparser.parse(link)
            if showfeeds:
                print(d['entries'][0].keys())
            if not category in feeds:
                feeds[category] = []
                feeds[category].append(d)

            else:
                feeds[category].append(d)




            # for item in d['entries']:
            #     if 'title' in item:
            #         pass#print(item['title'])
    return feeds


def getentry(outputkeys, adict):
    for key in outputkeys:
        if key in adict:
            return adict[key]

def outputtitles(feeds, outputcontentkeys = None, outputlinkkeys = None, filters = None):
    outputdict = {}
    for category in feeds:
        for feed in feeds[category]:
            #print(feed)
            for entry in feed['entries']:
                if outputcontentkeys:
                    entrytext = getentry(outputcontentkeys,entry)
                else:
                    entrytext = getentry(['title'], entry)
                if outputlinkkeys:
                    linktext = getentry(outputlinkkeys, entry)
                else:
                    linktext = getentry(['link'],entry)
                if not category in outputdict:
                    outputdict[category] = []
                    outputdict[category].append({'text': entrytext, 'linktext': linktext})
                else:
                    outputdict[category].append({'text': entrytext, 'linktext': linktext})

    return outputdict

def filter(outputdict, category, searchterms):
    newitems = []
    for article in outputdict[category]:
        for term in searchterms:
            if term in article['text']:
                newitems.append(article)
    return newitems
#pprint.pprint(getlinks())
#pprint.pprint(getrssfeeds(getlinks()))
#pprint.pprint((outputtitles(getrssfeeds(getlinks()), ['title'],['link'])))

if __name__ == "__main__":
    def example():
        d = feedparser.parse("http://www.technologyreview.com/topnews.rss")

        enteries = d['entries']
        for entry in enteries:
            print(entry['title'])
            print(entry['link'])
            # print(entry['content'][0]['value'])
            # for val in entry['content']:
            #     print(val['value'])


