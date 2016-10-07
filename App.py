'''
App.py
A starting class with most of the functionality that ties everything together
'''
import os
import hashlib
from datetime import datetime

import requests

import Config

def searchDocument(content):
	querys = Config.QUERYS
	matches = []
	for query in querys:
		if contents.find(query) != -1:
			matches.append(query.upper() + ": MATCHED")
		else:
			matches.append(query.upper() + ": NOT MATCHED")
	return matches

def searchDocumentForLinks(contents):
	query = ['<a', 'href=']
	searchContents = contents
	matches = []
	attempt = 1
	while len(searchContents) > 0:
		print('Attempt: ' + str(attempt))
		print('Content length: ' + str(len(searchContents)))
		linkIndex = searchContents.find(query[0])
		if linkIndex != -1:
			print('Query 0 matched at ' + str(linkIndex))
			searchContents = searchContents[linkIndex:]
			hrefIndex = searchContents.find(query[1])
			if hrefIndex != -1:
				print('Query 1 matched at ' + str(hrefIndex) + ' ' + searchContents[:hrefIndex + 15])
				searchContents = searchContents[hrefIndex:]

				doubleQuote = searchContents.find('\"')
				print(doubleQuote)
				singleQuote = searchContents.find('\'')
				print(singleQuote)
				openQuote = doubleQuote
				if singleQuote == -1 or (doubleQuote != -1 and doubleQuote < singleQuote):
					print('Double')
					doubleQuote = searchContents[openQuote+1:].find('\"')
					closeQuote = doubleQuote + openQuote
				else:
					print('Single')
					openQuote = singleQuote
					singleQuote = searchContents[openQuote+1:].find('\'')
					closeQuote = singleQuote + openQuote

				print('Open: ' + str(openQuote))
				print('Close: ' + str(closeQuote))
				matches.append(searchContents[openQuote+1:closeQuote+1])

				searchContents = searchContents[openQuote + closeQuote:]
			else:
				break
		else:
			break
		attempt = attempt + 1

	return matches

def downloadDocument(w, url):
	try:
		req = requests.get(url)
		w.status_code(req.status_code)
		w.body_callback(req.content)
	except Exception:
		return False
	return True

def removeProtocol(url):
	if(url.startswith('https://')):
		return url[8:]
	elif(url.startswith('http://')):
		return url[7:]
	else:
		return url

def hasFileExtension(url):
	afterFinalSlash = url[url.rfind('/'):]
	if afterFinalSlash.find('.html') == -1 or afterFinalSlash.find('.php') == -1:
		return False
	return True

def removeFileFromDir(url):
	if hasFileExtension(url):
		return url[:url.find('/')+1]
	return url

def removeDir(url):
	if removeProtocol(url).find('/') != -1:
		if url[::-1].find('/') == 0:
			url = url[::-1][1:][::-1]
		url = url[:url.rfind('/')] + '/'
	return url

def addTrailingSlash(url):
	if url[::-1][0:1] != '/':
		return url + '/'
	return url

def processRelativeLink(link, previousUrl):
	previousDir = removeFileFromDir(previousUrl)
	previousDir = addTrailingSlash(previousDir)
	if link.startswith('./'):
		return previousDir + link[2:]
	elif link.startswith('/'):
		return previousDir + link[1:]
	elif link.startswith('../'):
		while link.find('../') != -1:
			previousDir = removeDir(previousDir)
			link = link[3:]
		return previousDir + link;
	else:
		return link

class WebCrawler:
	def __init__(self):
		self.contents = ''
		self.status = ''

	def body_callback(self, buf):
		self.contents = buf

	def status_code(self, status):
		self.status = status

start_time = datetime.now()

w = WebCrawler()

if not os.path.exists('./cache'):
	os.makedirs('./cache')

if not os.path.exists('./blacklist'):
	os.makedirs('./blacklist')


BLACKLIST_DIR = os.getcwd() + '/blacklist/'
CACHE_DIR = os.getcwd() + '/cache/'

urls = []

urlsToProcess = []
for url in Config.ROOT_SITES:
	urlsToProcess.append(url)

previousUrl = ''

for url in urlsToProcess:
	urlsToProcess.remove(url)
	if url in urls:
		pass
	previousUrl = url
	urlNoProto = removeProtocol(url)
	fileName = 'index.html'

	if not hasFileExtension(url):
		urlNoProto = urlNoProto.replace('.', '/')
		urlNoProto = addTrailingSlash(urlNoProto)
	else:
		splitUrl = urlNoProto.split('.')
		urlNoProto = ''
		urlNoProto = splitUrl[0] + '/'
		for i in range(1, len(splitUrl)-2):
			urlNoProto = url + '/'

		urlNoProto = urlNoProto + splitUrl[len(splitUrl)-2].split('/')[0] + '/'

		fileName = splitUrl[len(splitUrl)-2].split('/')[1] + '.' + splitUrl[len(splitUrl)-1]

	if not os.path.exists(CACHE_DIR + urlNoProto):
		os.makedirs(CACHE_DIRS + urlNoProto)

	is_blacklisted = False
	try:
		with open(BLACKLIST_DIR + urlNoProto + fileName, 'w+b') as blacklist:
			is_blacklisted = True
	except:
		is_blacklisted = False

	if not is_blacklisted:
		with open(CACHE_DIR + urlNoProto + fileName, 'w+b') as file:
			print('Opened')
			print('Downloading: ' + url)
			if downloadDocument(w, url):
				print('Downloaded')
				print(w.status)
				if os.path.isfile(file.name):
					print('File exists')
					if hashlib.md5(file.read()) != hashlib.md5(w.contents):
						print('File Changed')
						file.write(w.contents)
						print('Wrote File')
				else:
					print('New File')
					file.write(w.contents)
					print('Wrote File')
					matches = searchDocument(w.contents)
					for match in matches:
						print(match)
				links = searchDocumentForLinks(w.contents)
				print(str(len(links)) + ' links were found! Adding unique links to urls')
				for link in links:
					link = processRelativeLink(link, previousUrl)
					if not link in urls:
						print('Link: ' + link)
						urlsToProcess.append(link)
						urls.append(link)

print('Elapsed Time: ' + str(datetime.now() - start_time))
print('Done!')