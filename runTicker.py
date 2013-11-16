#!/usr/bin/python

import json
import httplib
import os, math, datetime, time, sys

pipeLocation = ['~/g15Output']
graphFile = './pricegraph.json'
graph = []
numScreens = 4
currCode = 'AUD'



#if not os.path.exists(pipeLocation):
#	print 'Pipe location incorrect; fatal'
#	sys.exit()

def bitcoinCharacterCommand(x,y):
	bmap = [[1,3],[0,1,2,3],[1,4],[1,2,3],[1,4],[0,1,2,3],[1,3]]
	messages = []
	for i in range(len(bmap)):
		for j in bmap[i]:
			messages.append("PS %d %d 1" % (x+j, y+i))
	return messages
	
def bitcoinBig(x,y):
	bmapTop = [[2,3,5,6],[2,3,5,6],[0,1,2,3,4,5,6,7],[0,1,2,3,4,5,6,7,8],[2,3,7,8],[2,3,7,8],[2,3,4,5,6,7,8]]
	bmap = bmapTop + [[2,3,4,5,6,7]] + bmapTop[::-1]
	messages = []
	for i in range(len(bmap)):
		for j in bmap[i]:
			messages.append("PS %d %d 1" % (x+j, y+i))
	return messages

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
	t = 'TO 0 35 1 0 "%s"' % timestring
	return [t]
		
def drawGraph(timeMul=1):
	# timeMul is how many items to average over each time.
	# timeMul = 3 would mean each step 
	# graphWidth steps total, normally covering 40 minutes. To cover 12 hours you'll need 0.3 hours as your time mul, or 20ish
	global graph
	# bounds are the right hand side, top
	boundX = 136
	boundY = 3
	height = 33
	graphWidth = 55
	allPrices = [a[1] for a in graph[:timeMul*graphWidth]]
	minPrice = min(allPrices)
	maxPrice = max(allPrices)
	minmax = (minPrice, maxPrice)
	rangePrice = maxPrice - minPrice
	genericMessage = 'DL %d %d %d %d %d'
	messages = []
	
	def getYForGraph(r):
		try:
			return (boundY+height) - (graph[r][1]-minPrice)/rangePrice*height
		except IndexError:
			return None
		
	def average(l):
		return 1.0*sum(l)/len(l)
		
	def group(size, toGroup):
		ret = []
		
	currX = boundX
	for r in range(1,graphWidth):
		x1 = currX
		x2 = currX+1
		y1s = []
		y2s = []
		for i in range(timeMul):
			y1s.append(getYForGraph(r*timeMul+i))
			y2s.append(getYForGraph((r-1)*timeMul+i))
		
		if None not in (y1s+y2s):
			messages += [genericMessage % (x1,int(average(y1s)),x2,int(average(y2s)),1)]
		currX -= 1
	messages += ['TO %d %d 0 2 "%5.1f"' % (boundX, boundY, max(minmax))]
	messages += ['TO %d %d 0 2 "%5.1f"' % (boundX, boundY+height-5, min(minmax))]
	messages += ['TO %d %d 0 0 "%d min"' % (boundX-graphWidth/2-4, boundY+height+2, timeMul*graphWidth)]
	return messages
	
def sendCommand(com,locIndex=0):
	os.system('echo \'%s\' > %s' % (com,pipeLocation[locIndex]))
	
def sendMany(coms,locIndex=0):
	print 'SendMany to %d' % locIndex
	sendCommand('MC 1',locIndex)
	for toSend in coms:
		sendCommand(toSend,locIndex)
	sendCommand('MC 0',locIndex)
	
def sendScreens(screens):
	i = 0
	for screen in screens:
		sendMany(screen,i)
		i += 1

for i in range(numScreens-1):
	p = './g15-b%d' % i
	pipeLocation.append(p)
	sendCommand('SN "%s"' % p)

priceData = httplib.HTTPSConnection('api.coindesk.com')
priceData.request("GET",'/v1/bpi/currentprice/%s.json' % currCode)
r1 = priceData.getresponse()
data = json.loads(r1.read())

loadGraph()
updateGraph(data['bpi'][currCode]['rate_float'])
saveGraph()

CURRS = ['AUD','USD']
maxDigits = int(math.ceil(math.log(max([data['bpi'][CURR]['rate_float'] for CURR in CURRS]))/math.log(10)))

for i in range(numScreens):
	toRet = []
	toRet += ['BPI','']
	for CURR in CURRS:
		toRet += [str(' :%'+str(maxDigits+3)+'.2f%s') % (data['bpi'][CURR]['rate_float'], CURR[:2])]
	
	allToSend = [
		'TL ' + ' '.join(['"%s"' % m for m in toRet]),
		'TO 0 8 1 0 "By CoinDesk"'
		]
		
	allToSend += drawGraph([1,6,24,24*7][i])
	allToSend += printTime()
	allToSend += bitcoinBig(0,16)

	sendMany(allToSend,i)
	
