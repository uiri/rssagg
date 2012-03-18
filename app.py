from flask import Flask, render_template, request
import feedparser, os, time, copy, threading

app = Flask(__name__)
app.votes = {}
feeds = []
with open("urllist.conf") as conf:
    for line in conf:
        feeds.append(line)
app.debug = True
items to be more appropriate
app.title2url = {}
app.titlebydate = []
app.lastcheck = 0

def refresh():
    linktitle = []
    datetitle = []
    for feed in feeds:
        print "Reading " + feed
        d = feedparser.parse(feed)
        offset = 0
        if time.mktime(d.entries[0].date_parsed) > time.time():
            offset = 14400
        for entry in d.entries:
            realdate = time.mktime(entry.date_parsed)
            realdate -= offset
            linktitle.append([entry.title, entry.link])
            for i in xrange(len(datetitle)):
                if datetitle[i][1] < realdate:
                    datetitle.insert(i, [entry.title, realdate])
                    break
            if [entry.title, realdate] not in datetitle:
                datetitle.append([entry.title, realdate])
    app.titlebydate = []
    for i in xrange(len(datetitle)):
        app.titlebydate.append(datetitle[i][0])
    app.title2url = dict(linktitle)
    app.lastcheck = int(time.time())

@app.route('/', methods=['GET', 'POST'])
def index():
    print request.headers['user-agent']
    titles = []
    links = []
    if (int(time.time()) - app.lastcheck) > 3500:
        refresh()
        app.lastcheck = time.time()
    for title in app.titlebydate:
        if len(titles) < 30:
            titles.append(title)
            links.append(app.title2url[title])
        else:
            break
    return render_template("index.html", titles=titles, links=links)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
