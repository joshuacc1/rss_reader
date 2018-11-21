from flask import Flask, jsonify, render_template, url_for, request
app = Flask(__name__)
import RSS_Manager.Source as src
import RSS_Manager.Feeds as fd
from database.DatabaseManagement import datalink
from database.DatabaseManagement import linksmanagement as lm
import datetime

base_url = r"http://127.0.0.1:5000/"

@app.route('/')
def homepage():
    urls = src.RSS_URL_Management()
    with datalink('rssdata','rsslinks') as mydata:
        for record in mydata.find({}):
            urls.addurl(record['category'],record['link'].replace(r'\n',''))

    return render_template('homepage.html', urls=urls.urls)

@app.route('/linksmanagement', methods=['POST','GET'])
def linksmanagement():
    urls = src.RSS_URL_Management()
    with datalink('rssdata','rsslinks') as mydata:
        for record in mydata.find({}):
            urls.addurl(record['category'],record['link'].replace(r'\n',''))

    if request.method == 'POST':
        lmg = lm()
        category = request.form['category']
        link = request.form['link']

        if request.form['addremove'] == 'add':
            lmg.addlink(category,link)
        elif request.form['addremove'] == 'remove':
            lmg.removelink(category=category,
                           link=link)
        choice = request.form['addremove']

        print(choice,category, link)

        urls = src.RSS_URL_Management()
        with datalink('rssdata', 'rsslinks') as mydata:
            for record in mydata.find({}):
                urls.addurl(record['category'], record['link'].replace(r'\n', ''))
        return render_template('homepage.html', urls=urls.urls)

    urls = src.RSS_URL_Management()
    with datalink('rssdata','rsslinks') as mydata:
        for record in mydata.find({}):
            urls.addurl(record['category'],record['link'].replace(r'\n',''))
    return render_template('linksmanagement.html', urls=urls.urls)

def stringtobool(val):
    if(val == 'True'):
        return True
    elif (val == 'False' or val == 'None'):
        return False
    else:
        return False

@app.route('/all')
def getallarticles(data=None,filterterm=None):
    rssdata = getrssdata(filterkey=None)
    return render_template('testhtml.html', data=rssdata)


@app.route('/filter/<filterterm>')
def getfilteredarticles(data=None, filterterm=None):
    rssdata = getrssdata(filterkey=filterterm)
    return render_template('testhtml.html', data=rssdata)

@app.route('/category/<category>')
def getcategory(data=None, category=None, filterterm=None):
    rssdata = getrssdata(filterkey=request.args.get('filterkey'),
                         filtervalue=request.args.get('filtervalue'),
                         selectcategory=category,
                         summaryflag=stringtobool(request.args.get('summaryflag')),
                         authorflag=stringtobool(request.args.get('authorflag')))
    return render_template('testhtml.html', data=rssdata)

@app.route('/category/<category>/<filterkey>')
def getcategoryfiltered(data=None, category=None, filterterm=None):
    selectcategory = 'nasa'
    params = {'summary': False}
    print(request.args)
    rssdata = getrssdata(filterkey=request.args.get('filterkey'),selectcategory=category, summaryflag=request.args.get('summaryflag'))
    return render_template('testhtml.html',  data=rssdata)

def getrssdata(filterkey=None, filtervalue=None,selectcategory=None, summaryflag=True, authorflag=True):
    urls = src.RSS_URL_Management()
    if not filtervalue:
        filterkey = 'summary'
    with datalink('rssdata','rsslinks') as mydata:
        for record in mydata.find({}):
            urls.addurl(record['category'],record['link'].replace(r'\n',''))

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
                        if filtervalue is None or filtervalue in entry[filterkey]:
                            pubtime = datetime.datetime(*entry['published_parsed'][0:7])
                            if pubtime > (datetime.datetime.today() - datetime.timedelta(2)):
                                newfeed['source'] = feed.content['feed']['title']
                                newfeed['link'] = entry['link']
                                newfeed['title'] = entry['title']
                                newfeed['time'] = entry.get('published')
                                if summaryflag:
                                    if 'summary' in entry:
                                        newfeed['summary'] = entry['summary']
                                if authorflag:
                                    if 'author' in entry:
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
                        if filtervalue is None or filtervalue in entry[filterkey]:
                            pubtime = datetime.datetime(*entry['published_parsed'][0:7])
                            if pubtime > (datetime.datetime.today() - datetime.timedelta(2)):
                                newfeed['source'] = feed.content['feed']['title']
                                newfeed['link'] = entry['link']
                                newfeed['title'] = entry['title']
                                newfeed['time'] = entry.get('published')
                                if summaryflag:
                                    if 'summary' in entry:
                                        newfeed['summary'] = entry['summary']
                                if authorflag:
                                    if 'author' in entry:
                                        newfeed['author'] = entry['author']
                                datadict[selectcategory].append(newfeed)
                except:
                    pass


    return datadict

with app.test_request_context():
    print(url_for('static', filename='style.css'))
    print(url_for('getcategory', category='technology'))
    print(getrssdata(selectcategory="politics"))


@app.route('/hello')
def hello_world2():
    return 'dont say hi to me'