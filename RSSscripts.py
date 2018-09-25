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
    selectcategory = 'politics'
    filterkey = 'Woman'

    HTTPHead = """
    <Head>
        <Body>

     """
    HTTPMid = ""
    HTTPBottom = """
        </Body>
    </Head>

    """

    # HTTPHead = """
    # <!DOCTYPE html>
    # <html lang="en">
    # <head>
    # <title>CSS Template</title>
    # <meta charset="utf-8">
    # <meta name="viewport" content="width=device-width, initial-scale=1">
    # <style>
    # * {
    #     box-sizing: border-box;
    # }
    #
    # body {
    #     font-family: Arial, Helvetica, sans-serif;
    # }
    #
    # /* Style the header */
    # header {
    #     background-color: #666;
    #     padding: 30px;
    #     text-align: center;
    #     font-size: 35px;
    #     color: white;
    # }
    #
    # /* Create two columns/boxes that floats next to each other */
    # nav {
    #     float: left;
    #     width: 30%;
    #     height: 300px; /* only for demonstration, should be removed */
    #     background: #ccc;
    #     padding: 20px;
    # }
    #
    # /* Style the list inside the menu */
    # nav ul {
    #     list-style-type: none;
    #     padding: 0;
    # }
    #
    # article {
    #     float: left;
    #     padding: 20px;
    #     width: 70%;
    #     background-color: #f1f1f1;
    #     height: 300px; /* only for demonstration, should be removed */
    # }
    #
    # /* Clear floats after the columns */
    # section:after {
    #     content: "";
    #     display: table;
    #     clear: both;
    # }
    #
    # /* Style the footer */
    # footer {
    #     background-color: #777;
    #     padding: 10px;
    #     text-align: center;
    #     color: white;
    # }
    #
    # /* Responsive layout - makes the two columns/boxes stack on top of each other instead of next to each other, on small screens */
    # @media (max-width: 600px) {
    #     nav, article {
    #         width: 100%;
    #         height: auto;
    #     }
    # }
    # </style>
    # </head>
    # <body>
    # <header>
    #   <h2>Cities</h2>
    # </header>
    #
    # <section>
    #   <nav>
    #     <ul>
    # """
    #
    # HTTPBottom = """
    #     </ul>
    #       </nav>
    #
    #       <article>
    #         <h1>link to article here</h1>
    #       </article>
    #     </section>
    #
    #     <footer>
    #       <p>Footer</p>
    #     </footer>
    #     </body>
    #     </html>
    # """

    with open('rsslinks.txt') as links:
        for link in links:
            category, link = tuple(link.split(','))
            urls.addurl(category,link.replace(r'\n',''))

    with open('output.htm','w') as httpfile:
        myfeeds = fd.feeds()
        for category in urls.getcategories():
            [myfeeds.addfeed(fd.feed(url,category)) for url in urls.geturls(category)]

        httpfile.write(HTTPHead)

        httpfile.write(selectcategory + '\n')
        for feed in myfeeds.getfeeds(selectcategory):

            feed.getfeed()

            for entry in feed.getvalue('entries'):
                if filterkey is None or filterkey in entry['title']:
                    httpfile.write(''.join(['<div>', feed.content['feed']['title'], " - ",
                                             '<a href=', entry['link'], '>',entry['title'],'</a>',
                                             '</div>\n']))
        httpfile.write(HTTPBottom)

#getRSSfeedsandoutput()
getRSSfeedsandoutputtoHTTP()