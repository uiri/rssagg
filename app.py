from flask import Flask, render_template, request
import feedparser, os, time, copy

app = Flask(__name__)
feeds = []
app.votes = {}
app.debug = True
feeds = []
with open("urllist.conf") as conf:
    for line in conf:
        feeds.append(line)
app.title2url = {}
app.titlebydate = []
app.lastcheck = 0

def refresh():
    linktitle = []
    votetitle = []
    datetitle = []
    for feed in feeds:
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
            if app.votes != {}:
                if entry.title in app.votes:
                    votetitle.append([entry.title, app.votes[entry.title]])
                else:
                    votetitle.append([entry.title, 1])
            else:
                votetitle.append([entry.title, 1])
    app.titlebydate = []
    for i in xrange(len(datetitle)):
        app.titlebydate.append(datetitle[i][0])
    app.votes = dict(votetitle)
    app.title2url = dict(linktitle)
    app.lastcheck = int(time.time())

def calc(vote, index):
    index += 1
    return vote / pow(index, 0.2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        plusoneto = request.form.get('l', '')
        app.votes[plusoneto] += 1
    vals = {}
    titles = []
    links = []
    if (int(time.time()) - app.lastcheck) > 3600:
        refresh()
    for i in xrange(len(app.titlebydate)):
        vals[app.titlebydate[i]] = calc(app.votes[app.titlebydate[i]], i)
    sortedvals = sorted(vals, key=vals.get, reverse=True)
    for title in sortedvals:
        if len(titles) < 30:
            titles.append(title)
            links.append(app.title2url[title])
            displayvotes.append(app.votes[title])
        else:
            break
    return render_template("index.html", titles=titles, links=links)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
