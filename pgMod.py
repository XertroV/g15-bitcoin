#!/usr/bin/python

import json
import httplib
import os, math, datetime, time

graphFile = './pricegraph.json'
	
def saveGraph():
	global graph
	with open(graphFile,'w') as f:
		f.write(json.dumps(graph))
		
with open(graphFile) as f:
	pg = json.loads(f.read())
now = int(time.time())
pgNew = [(now-i*60, pg[i]) for i in range(len(pg))]
graph = pgNew
print graph
test = raw_input('press enter to cont / ctrl c to cancel')
saveGraph()


