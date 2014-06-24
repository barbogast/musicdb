# run with `twistd -ny website.tac`

from twisted.application import service, internet
from nevow import appserver, rend, inevow, loaders, flat, static, tags as T
from nevow.url import URL
import psycopg2

import model01 as model
import simpleview_02 as simpleview


        

def mkModel():
    conn = psycopg2.connect(database='musicdb', user='musicdb')
    cur = conn.cursor()
    m = model.Model()
    m.setCursor(cur)
    return m
model = mkModel()

application = service.Application('musicdb site')
webservice = internet.TCPServer(8081, appserver.NevowSite(simpleview.IndexPage(model, debug=True)))
webservice.setServiceParent(application)