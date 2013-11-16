#!/usr/bin/python

import json
import httplib
import os, math, datetime, time, sys

pipeLocation = '~/g15Output'
graphFile = './pricegraph.json'
graph = []

#if not os.path.exists(pipeLocation):
#	print 'Pipe location incorrect; fatal'
#	sys.exit()

def loadGraph():
	global graph
	if os.path.exists(graphFile):
		with open(graphFile,'r') as f:
			graph = json.loads(f.read())
		
def updateGraph(newVal):
	global graph
	graph = [[int(time.time()), newVal]] + graph
	
def saveGraph():
	global graph
	with open(graphFile,'w') as f:
		f.write(json.dumps(graph))
		
def printTime():
	timestring = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %I:%M")
	t = 'TO 4 35 1 0 "%s"' % timestring
	return [t]
		
def drawGraph(timeMul):
	# timeMul is how many items to average over each time.
	# timeMul = 3 would mean each step 
	global graph
	# bounds are the right hand side, top
	boundX = 136
	boundY = 5
	height = 33
	graphWidth = 40
	allPrices = [a[1] for a in graph]
	minPrice = min(allPrices)
	maxPrice = max(allPrices)
	minmax = (minPrice, maxPrice)
	rangePrice = maxPrice - minPrice
	print rangePrice
	genericMessage = 'DL %d %d %d %d %d'
	messages = []
	
	def getYForGraph(r):
		try:
			return (boundY+height) - (graph[r][1]-minPrice)/rangePrice*height
		except IndexError:
			print r, graph
			return None
		
	currX = boundX
	for r in range(1,graphWidth):
		x1 = currX
		x2 = currX+1
		y1 = getYForGraph(r)
		y2 = getYForGraph(r-1)
		if None not in [y1,y2]:
			messages += [genericMessage % (x1,int(y1),x2,int(y2),1)]
		currX -= 1
	messages += ['TO %d %d 0 2 "%5.1f"' % (boundX-1, boundY-2, max(minmax))]
	messages += ['TO %d %d 0 2 "%5.1f"' % (boundX-1, boundY-2+height, min(minmax))]
	return messages
	
def sendCommand(com):
	print com
	os.system('echo \'%s\' > %s' % (com,pipeLocation))

currCode = 'AUD'
priceData = httplib.HTTPSConnection('api.coindesk.com')
priceData.request("GET",'/v1/bpi/currentprice/%s.json' % currCode)
r1 = priceData.getresponse()
data = json.loads(r1.read())

loadGraph()
updateGraph(data['bpi'][currCode]['rate_float'])

CURRS = ['AUD','USD']
maxDigits = int(math.ceil(math.log(max([data['bpi'][CURR]['rate_float'] for CURR in CURRS]))/math.log(10)))

toRet = []
toRet += ['BPI-CoinDesk','']
for CURR in CURRS:
	toRet += [str('%s: %'+str(maxDigits+3)+'.2f') % (CURR, data['bpi'][CURR]['rate_float'])]


allToSend = [
	'MC 1',
	'TL ' + ' '.join(['"%s"' % m for m in toRet]),
	]
		
saveGraph()

allToSend += drawGraph(1)
allToSend += printTime()

allToSend += ['MC 0']	
	
for toSend in allToSend:
	sendCommand(toSend)
	
