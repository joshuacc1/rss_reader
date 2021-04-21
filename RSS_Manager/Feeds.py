import RSS_Manager.Source
import feedparser



class feed():
    def __init__(self, url, category = None, getfeed = True):
        self.url = url
        self.category = category
        self.tags = []
        self.content = {}
        self.nltk = None

        if getfeed:
            self.getfeed()

    def getfeed(self):
        self.content = feedparser.parse(self.url)
        if self.category:
            for entry in self.content['entries']:
                entry['acategory'] = self.category

    def gettitles(self):
        return [t['title'] for t in self.content['entries']]

    def getsummaries(self):
        return [t['summary'] for t in self.content['entries']]

    def getenteries(self):
        return [t for t in self.content['entries']]

    def entries(self,args, filterterms = None):
        if not self.content:
            self.getfeed()
        entries = []
        for entry in self.content['entries']:
            if self.entryvalid(entry, args, filterterms):
                data = {arg: entry[arg] for arg in args}
                entries.append(data)
        return entries

    def entryvalid(self, entry, args, filterterms):
        for arg in args:
            if not arg in entry:
                return False

        if not filterterms:
            return True

        for arg in filterterms:
            if arg in filterterms:
                if filterterms[arg] in entry[arg]:
                    return True
        return False

    def getvalue(self,key):
        return self.content[key]

    def __str__(self):
        return self.url

class feeds():
    def __init__(self):
        self.feeds = {}
        self._itercounter = 0
        self._iterfeed = None

    def addfeed(self, urlfeed):
        if isinstance(urlfeed,feed):
            self.appendtokey(self.feeds,urlfeed.category,urlfeed)

    def appendtokey(self, srcdict, key, item):
        if key in srcdict:
            srcdict[key].append(item)
        else:
            srcdict[key] = []
            srcdict[key].append(item)

    def getfeeds(self, category = None):
        if category:
            return self.feeds[category]
        else:
            categories = [cat for cat in self.getcategories()]
            allfeeds = []
            for cat in categories:
                allfeeds.extend(self.feeds[cat])
            return allfeeds


    def filterfeeds(self, filterkey):
        newfeeds = {}
        for cat in self.feeds:
            filterfeedlist = [x for x in self.feeds if filterkey in x['entry']['title']]

    def getcategories(self):
        return self.feeds.keys()

    def __iter__(self,feed):
        self._iterfeed = self.feeds[feed]
        return self

    def __next__(self):
        if self._itercounter > len(self._iterfeed):
            return StopIteration()
        else:
            return self._iterfeed



if __name__ == "__main__":
    from RSS_Manager import Source
    urls = Source.RSS_URL_Management()
    urls.addurl('technology',r'https://www.wired.com/feed/rss')
    myfeeds = feeds()
    for url in urls.urls['technology']:
        afeed = feed(url,'technology')
        afeed.getfeed()
        myfeeds.addfeed(afeed)
    for afeed in myfeeds.getfeeds():
        print(afeed.entries(['title','summary']))

