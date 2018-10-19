from flask import Flask, jsonify, render_template, url_for
app = Flask(__name__)
import RSS_Manager.Source as src
import RSS_Manager.Feeds as fd

@app.route('/')
def getallarticles(data=None,filterterm=None):
    selectcategory = 'nasa'

    rssdata = getrssdata(filterkey=None)
    return render_template('testhtml.html', data=rssdata)


@app.route('/filter/<filterterm>')
def getfilteredarticles(data=None, filterterm=None):
    selectcategory = 'nasa'

    rssdata = getrssdata(filterkey=filterterm)
    return render_template('testhtml.html', data=rssdata)

@app.route('/category/<category>')
def getcategory(data=None, category=None, filterterm=None):
    selectcategory = 'nasa'

    rssdata = getrssdata(filterkey=filterterm,selectcategory=category)
    return render_template('testhtml.html', data=rssdata)

@app.route('/category/<category>/<filterterm>')
def getcategoryfiltered(data=None, category=None, filterterm=None):
    selectcategory = 'nasa'

    rssdata = getrssdata(filterkey=filterterm,selectcategory=category)
    return render_template('testhtml.html',  data=rssdata)

def getrssdata(filterkey=None, selectcategory=None):
    urls = src.RSS_URL_Management()
    with open('rsslinks.txt') as links:
        for link in links:
            category, link = tuple(link.split(','))
            urls.addurl(category,link.replace(r'\n',''))

    myfeeds = fd.feeds()
    for category in urls.getcategories():
        [myfeeds.addfeed(fd.feed(url,category)) for url in urls.geturls(category)]
    datadict = {}

    if selectcategory:
        if selectcategory in myfeeds.getcategories():
            datadict[selectcategory] = []
            for feed in myfeeds.getfeeds(selectcategory):
                feed.getfeed()
                try:
                    for entry in feed.getvalue('entries'):
                        newfeed = {}
                        if filterkey is None or filterkey in entry['summary']:
                            newfeed['source'] = feed.content['feed']['title']
                            newfeed['link'] = entry['link']
                            newfeed['title'] = entry['title']
                            newfeed['summary'] = entry['summary']
                            newfeed['author'] = entry['author']
                            datadict[selectcategory].append(newfeed)
                except:
                    pass

    else:
        for category in myfeeds.getcategories():
            datadict[category] = []
            for feed in myfeeds.getfeeds(category):
                feed.getfeed()
                try:
                    for entry in feed.getvalue('entries'):
                        newfeed = {}
                        if filterkey is None or filterkey in entry['summary']:
                            newfeed['source'] = feed.content['feed']['title']
                            newfeed['link'] = entry['link']
                            newfeed['title'] = entry['title']
                            newfeed['summary'] = entry['summary']
                            newfeed['author'] = entry['author']
                            datadict[category].append(newfeed)
                except:
                    pass


    return datadict

with app.test_request_context():
    print(url_for('static', filename='style.css'))
    print(url_for('getcategory', category='technology'))


@app.route('/hello')
def hello_world2():
    return 'dont say hi to me'