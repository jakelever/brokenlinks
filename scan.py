import requests
import argparse
import re
from urllib.parse import urljoin
from collections import defaultdict

def urlWorks(url):
	try:
		r = requests.get(url)
		return r.url, r.status_code == 200
	except:
		return False, False

def getHTML(url):
	r = requests.get(url)
	if "text/html" in r.headers["content-type"]:
		return r.text
	else:
		return False

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Find broken links on a website given a URL')
	parser.add_argument('--url',required=True,type=str,help='URL to start from')
	parser.add_argument('--filter',required=False,type=str,help='Alternative filter to use on URLs on whether to scan them as well')
	parser.add_argument('--log',required=True,type=str,help='Log file to output scan')
	args = parser.parse_args()

	firstURL, firstURLExists = urlWorks(args.url)
	assert firstURLExists
	toScan = [firstURL]
	done = set()

	if args.filter:
		filterURL = args.filter
	else:
		filterURL = args.url

	urlStatus = {}
	
	with open(args.log,'w') as outF:
		expectedAnchors = defaultdict(set)
		foundAnchors = defaultdict(set)

		while len(toScan) > 0:
			url = toScan.pop(0)
			done.add(url)
			html = getHTML(url)
			

			# Not an HTML file
			if html == False:
				continue

			print(url)

			#for link in re.finditer('<a(?P<attributes>.*?)>(?P<text>.*?)</a>',html):
			for link in re.finditer('<a.*?href="(?P<url>.*?)".*?>(?P<text>.*?)</a>',html):
				text = link.groupdict()['text']
				linkURL = link.groupdict()['url']

				#attributes = {}
				#for attribute in re.finditer('(?P<name>\w+)="(?P<value>.*?)"',link.groupdict()['attributes']):
				#	attributes[attribute.groupdict()['name']] = attribute.groupdict()['value']

				#if 'href' in attributes:
					#linkURL = attributes['href']
				if linkURL.startswith('mailto:'):
					continue


				#isAbsoluteURL = '://' in linkURL
				#if not isAbsoluteURL:
				# Let's get the absolute URL
				linkURL = urljoin(url,linkURL)

				#if linkURL[-1] == '/':
				#	linkURL = linkURL[:-1]

				if '#' in linkURL:
					location = linkURL.index('#')
					anchor = linkURL[(location+1):]
					linkURL = linkURL[:location]
					if linkURL.startswith(filterURL):
						expectedAnchors[linkURL].add(anchor)

				#print(linkURL)
				if not linkURL in urlStatus:
					urlStatus[linkURL] = urlWorks(linkURL)
				replaceURL, exists = urlStatus[linkURL]
				if exists:
					linkURL = replaceURL

				outF.write("LINK\t%s\t%s\t%s\n" % (url, linkURL, str(exists)))

				if linkURL.startswith(filterURL) and not linkURL in done and not linkURL in toScan:
					toScan.append(linkURL)

				#if 'id' in attributes:
				#	foundAnchors[url].add(attributes['id'])

			for ids in re.finditer('\W(name|id)="(?P<id>.*?)"',html):
				anchorID = ids.groupdict()['id']
				#print(url, anchorID)
				foundAnchors[url].add(anchorID)
				#print("FOUND\t%s\t%s" % (url, anchorID))

		for url,anchors in expectedAnchors.items():
			for anchor in sorted(list(anchors)):
				found = anchor in foundAnchors[url]
				outF.write("ANCHOR\t%s\t%s\t%s\n" % (url,anchor,str(found)))
