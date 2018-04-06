import sqlite3
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from settings import *

conn = sqlite3.connect(DB_NAME)
conn.isolation_level = None
curs = conn.cursor()

class InvalidURLError(Exception):
    pass

def find_index(item, lst):
    for i, itm in enumerate(lst):
        if itm == item:
            return i
    return None

def get_ids():
    return [i[0] for i in curs.execute('SELECT id FROM pages WHERE done = 0 ORDER BY id;')]

def get_url(id_):
    return [i[0] for i in curs.execute('SELECT url FROM pages WHERE id = ?;', (id_,))][0]

def extend_info(id_, title, content, linksto):
    curs.execute('UPDATE pages SET title = ?, done = 1, content = ?, linksto = ? WHERE id = ?;', (title, content, 
','.join(linksto), id_))
    conn.commit()

def get_title(soup):
    return soup.find('title').get_text()

def see_later(urls):
    for url in urls:
        try:
            curs.execute('INSERT INTO pages VALUES ((SELECT MAX(id) FROM pages) + 1, ?, 0, \'\', \'\', \'\')', (url,))
        except sqlite3.IntegrityError:
            continue
    conn.commit()

def get_links(soup):
    links = []
    for link in soup.find_all('a'):
        try:
            links.append(link.attrs['href'])
        except KeyError:
            continue
    return links

def process_url(url, original):
    # print(url, original, end=' ', flush=True)
    url = url.split('?')[0]
    if url[0] == '#':
        raise IndexError
    parsed = urlparse(original)
    # url.replace('//', parsed.scheme + '://')
    if url[:2] == '//':
        url = parsed.scheme + ':' + url
    if url[0] == '/' and url[1] != '/':
        url = parsed.scheme + '://' + parsed.netloc + url
    # print(url)
    return url

def remove_task(id_):
    curs.execute('DELETE FROM pages WHERE id = ?', (id_,))

def print_all_urls(urls, heading=None):
    if heading is None:
        print('found:')
    else:
        print(heading)
        heading = None
    for url in urls:
        print(url)

try:
    while True:
        for id_ in get_ids():
            url = get_url(id_)
            print(id_, url, end='...', flush=True)
            if url.endswith('.pdf') or url.startswith('javascript:') or url.startswith('#'):
                print('wrong format')
                remove_task(id_)
                continue
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                r.encoding = r.apparent_encoding
            except requests.exceptions.RequestException:
                print('failed', flush=True)
                remove_task(id_)
                continue
            except KeyboardInterrupt:
                ch = input('e/c?')
                if ch == 'e':
                    print('quit')
                    conn.commit()
                    conn.close()
                    quit()
                elif ch == 'c':
                    print('cancelled')
                    remove_task(id_)
                    continue
            print('succeed')
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                title = get_title(soup)
            except AttributeError:
                remove_task(id_)
                continue
            links = get_links(soup)
            print('title:', title)
            # print_all_urls(links)
            bad_links = []
            for i, link in enumerate(links):
                try:
                    links[i] = process_url(link, url)
                except IndexError:
                    bad_links.append(links[i])
            for link in bad_links:
                try:
                    del links[find_index(link, links)]
                except:
                    pass
            print_all_urls(links)
            extend_info(id_, title, r.text, links)
            see_later(links)
except KeyboardInterrupt:
    conn.commit()
    conn.close()
