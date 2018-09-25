

class RSS_URL_Management:
    def __init__(self):
        self.urls = {}
        self.index = 0

    def addurl(self,category, url):
        self.appendtokey(self.urls,category,url)

    def geturls(self, category):
        return self.urls[category]

    def filterurls(self, filterkey, category = None ):
        filteredlinks = {}
        for cat in self.urls:
            listofurls = [url for url in self.urls[cat] if filterkey in url]
            filteredlinks[cat] = listofurls
        newrssurlman = RSS_URL_Management()
        newrssurlman.urls = filteredlinks
        return newrssurlman

    def appendtokey(self, srcdict, key, item):
        if key in srcdict:
            srcdict[key].append(item)
        else:
            srcdict[key] = []
            srcdict[key].append(item)

    def getcategories(self):
        return self.urls.keys()