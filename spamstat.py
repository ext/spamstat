#!/usr/bin/env python

import os
import sys
import email
import email.parser
import email.utils
import re
import sqlite3
import datetime, time
import pylab

if len(sys.argv) != 2:
    print 'Usage: spamstat.py PATH'
    sys.exit(1)

path = sys.argv[1]
conn = sqlite3.connect('spamstat.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS spam (file TEXT PRIMARY KEY, msgid TEXT, recv TEXT, date DATE)')

for f in os.listdir(path):
    fp = open(path + '/' + f)
    parser = email.parser.FeedParser()
    for line in fp:
        if line == "\n":
            message = parser.close()
            break
        parser.feed(line)
    fp.close()

    id = message['Message-ID']
    to = email.utils.parseaddr(message['To'])[1]
    date_raw = email.utils.parsedate(message['Date'])
    if date_raw:
        date = time.mktime(date_raw)
    else:
        date = time.time()

    row = (f, id, to, date)
    c.execute('REPLACE INTO spam VALUES (?,?,?,?)', row)

conn.commit()

entries = {'Other' : 0}
n = 0
max = 9
for row in c.execute("select recv, count(*) as n from spam group by recv order by n desc"):
    if n < max:
        entries[row[0]] = row[1]
    else:
        entries['Other'] += row[1]
    n += 1

pylab.figure(1, figsize=(8.5,6))
ax = pylab.axes([0.15, 0.1, 0.5, 0.7])

labels = entries.keys()
fracs = entries.values()

pylab.pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True, colors=('b', 'g', 'r', 'c', 'm', 'y', 'w', (1,0.5,1), (0.7,0.3,0.3), (0.3,0.3,0.7)))
pylab.title('Spam per address', bbox={'facecolor':'0.8', 'pad':5})

pylab.savefig('test.png')


