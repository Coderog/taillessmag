from flask import Flask, redirect, url_for, request, render_template
from urllib.parse import quote_plus, unquote_plus
from operator import itemgetter
from time import time
import sqlite3

SLIDE_MIN = 1
SLIDE_MAX = 16

conn = sqlite3.connect('pages.db')
conn.isolation_level = None
curs = conn.cursor()

def url2title(url):
    return [i[0] for i in curs.execute('SELECT title FROM pages WHERE url = ?', (url,))][0]

def pagerank(graph, damping=0.85, epsilon=1.0e-8):
    inlink_map = {}
    outlink_counts = {}

    def new_node(node):
        if node not in inlink_map:
            inlink_map[node] = set()
        if node not in outlink_counts:
            outlink_counts[node] = 0

    for tail_node, head_node in graph:
        new_node(tail_node)
        new_node(head_node)
        if tail_node == head_node:
            continue
        if tail_node not in inlink_map[head_node]:
            inlink_map[head_node].add(tail_node)
            outlink_counts[tail_node] += 1

    all_nodes = set(inlink_map.keys())

    for node, outlink_count in outlink_counts.items():
        if outlink_count == 0:
            outlink_counts[node] = len(all_nodes)
            for l_node in all_nodes:
                inlink_map[l_node].add(node)

    initial_value = 1 / len(all_nodes)
    ranks = {}

    for node in inlink_map.keys():
        ranks[node] = initial_value

    new_ranks = {}
    delta = 1.0

    while delta > epsilon:
        new_ranks = {}

        for node, inlinks in inlink_map.items():
            new_ranks[node] = ((1 - damping) / len(all_nodes)) + (damping * sum(ranks[inlink] / outlink_counts[inlink] for
                inlink in inlinks))

        delta = sum(abs(new_ranks[node] - ranks[node]) for node in new_ranks.keys())
        ranks, new_ranks = new_ranks, ranks
    return ranks

def build_map(sql_results):
    map = []
    urls = []
    for result in sql_results:
        urls.append(result[0])
    for result in sql_results:
        for outlink in result[2].split(','):
            if outlink in urls:
                map.append((result[0],outlink))
    return map

def search(query):
    # firststage = [i for i in curs.execute('SELECT url, title, linksto FROM pages WHERE title LIKE ? OR content LIKE ?',
    #     ('%{query}%'.format(query=query.replace('%', '\%').replace(' ', '%')), '%{query}%'.format(query=query.replace('%', '\%').replace(' ', '%'))))]
    firststage = [i for i in curs.execute('SELECT url, title, linksto FROM pages WHERE title LIKE ?',
        ('%{query}%'.format(query=query.replace('%', '\%').replace(' ', '%')),))]
    secondstage = build_map(firststage)
    try:
        thirdstage = pagerank(secondstage)
    except ZeroDivisionError:
        return []
    forthstage = sorted(thirdstage.items(), key=itemgetter(1), reverse=True)
    final = []
    for result in forthstage:
        print(result)
        try:
            title = url2title(result[0])
            if title:
                final.append((result[0], title))
        except:
            pass
    return final

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index_handler():
    if request.method == 'POST':
        if request.form.get('query'):
            return redirect(url_for('query_handler', query=quote_plus(request.form.get('query'))))
        else:
            return redirect(url_for('index_handler'))
    return render_template('index.html', imgurl=url_for('static', filename='search.svg'))

@app.route('/search/<query>/')
def query_handler(query):
    query = unquote_plus(query)
    query.replace('%', '\%')
    results = search(query)
    if len(results) == 0:
        return render_template('none.html', query=query, imgurl=url_for('static', filename='search.svg'))
    return render_template('result.html', query=query, length=len(results), results=results, imgurl=url_for('static', filename='search.svg'))

@app.route('/how-many/')
def how_many():
    return render_template('how-many.html', all=[i[0] for i in curs.execute('SELECT value FROM meta WHERE item = \'done\'')][0], acc=[i[0] for i in curs.execute('SELECT value FROM meta WHERE item = \'detailed\'')][0])
