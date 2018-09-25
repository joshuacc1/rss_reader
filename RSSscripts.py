import RSS_Manager.Source as src
import RSS_Manager.Feeds as fd

def getRSSfeedsandoutput():
    urls = src.RSS_URL_Management()

    with open('rsslinks.txt') as links:
        for link in links:
            category, link = tuple(link.split(','))
            urls.addurl(category,link.replace(r'\n',''))

    myfeeds = fd.feeds()
    for category in urls.getcategories():
        [myfeeds.addfeed(fd.feed(url,category)) for url in urls.geturls(category)]

    for feed in myfeeds.getfeeds('politics'):
        feed.getfeed()
        for entry in feed.getvalue('entries'):
            print(feed.category, ': ', entry['title'], entry['link'])

def getRSSfeedsandoutputtoHTTP():
    urls = src.RSS_URL_Management()
    selectcategory = 'nasa'
    filterkey = None

    HTTPHead = """
    <Head>
        <Body>
            <Style>
                .title {
                    font-size:150%;
                }
            </Style>
     """
    HTTPMid = ""
    HTTPBottom = """
        </Body>
    </Head>

    """

    with open('rsslinks.txt') as links:
        for link in links:
            category, link = tuple(link.split(','))
            urls.addurl(category,link.replace(r'\n',''))

    with open('output.htm','w') as httpfile:
        myfeeds = fd.feeds()
        for category in urls.getcategories():
            [myfeeds.addfeed(fd.feed(url,category)) for url in urls.geturls(category)]

        httpfile.write(HTTPHead)

        for category in myfeeds.getcategories():
            httpfile.write('<table style="width:100%">')
            httpfile.write('<tr><th style="width:100%; font-size:300%; text-align=center;">' + category + '</th><tr>')
            for feed in myfeeds.getfeeds(category):

                feed.getfeed()
                try:
                    for entry in feed.getvalue('entries'):
                        if filterkey is None or filterkey in entry['title']:
                            httpfile.write(''.join(['<tr>\n<th style="font-size:150%;">', feed.content['feed']['title'], "</th>\n<tr>",
                                                     '<tr>\n<td class="title">', '<a href=', entry['link'], '>',entry['title'],'</a>','</td>\n<tr>',
                                                     '<tr>\n<td>', entry['summary'],'</td>\n<tr>',
                                                    '<tr>\n<td>', entry['author'],'</td>\n<tr>']))
                except:
                    httpfile.write(''.join(['<tr>\n<th>', feed.content['feed']['title'], " - ", "</th>\n<tr>",
                                            '<tr>\n<td>', '<a href=', entry['link'], '>', entry['title'], '</a>',
                                            '</td>\n<tr>']))

        httpfile.write('</table>')
        httpfile.write(HTTPBottom)

#getRSSfeedsandoutput()
getRSSfeedsandoutputtoHTTP()