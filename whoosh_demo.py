# -*- coding: utf-8 -*-

import json

from flask import Flask
from flask import request
from gevent import pywsgi

from whoosh import qparser
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

from common import *

import os

app = Flask(__name__)

schema = Schema(content=TEXT(stored=True))
if not os.path.exists("index"):
    os.mkdir("index")
ix = create_in("index", schema)
writer = ix.writer()
for line in read_file("bot_resources/bot1/intents.txt"):
    writer.add_document(content=line)
writer.commit()
print("building index finished...")

searcher = ix.searcher()


@app.route('/search', methods=['GET', 'POST'])
def search():
    resq_data = json.loads(request.get_data())
    query = resq_data["query"].strip()

    qp = QueryParser("content", ix.schema)
    # qp.add_plugin(qparser.FuzzyTermPlugin())

    query = pre_process(query)
    # query = " ".join([w + "~" for w in query.split(" ")])

    print(query)
    query = qp.parse(query)
    print(query)

    results = searcher.search(query)

    res = []
    for r in results:
        res.extend(r.values())
    return {'code': 0, 'msg': 'success', 'data': res}


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8089), app)
    server.serve_forever()
