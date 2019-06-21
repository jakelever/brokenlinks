import requests
import argparse
import re
from urllib.parse import urljoin
from collections import defaultdict

def checkURL(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'}
		r = requests.get(url,headers=headers)
		if r.status_code == 200:
			return r.url
		else:
			return False
	except:
		return False

def getHTML(url):
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'}
	r = requests.get(url,headers=headers)
	if "text/html" in r.headers["content-type"] and r.status_code == 200:
		return r.text
	else:
		return False

def trimRight(s,toTrim):
	if s.endswith(toTrim):
		return s[:-len(toTrim)]
	else:
	 	return s

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Find broken links on a website given a URL')
	parser.add_argument('--url',required=True,type=str,help='URL to start from')
	parser.add_argument('--filter',required=False,type=str,help='Alternative filter to use on URLs on whether to scan them as well')
	parser.add_argument('--log',required=True,type=str,help='Log file to output scan')
	parser.add_argument('--all', action='store_true',help='Log all links, not just the links that fail')
	parser.add_argument('--images', action='store_true',help='Check images as well as links')
	parser.add_argument('--ghpages', action='store_true',help='Tidy up output for a GitHub pages site. Deal with the fact that github-pages does not require ignore .html at end of URLs')
	args = parser.parse_args()

	toScan = [args.url]
	done = set()

	if args.filter:
		filterURL = args.filter
	else:
		filterURL = args.url

	checkedURLs = {}
	checkedURLs[args.url] = checkURL(args.url)
	assert checkedURLs[args.url]

	log = {}
	links = defaultdict(list)
	foundAnchors = defaultdict(set)

	while len(toScan) > 0:
		sourceURL = toScan.pop(0)
		done.add(sourceURL)
		html = getHTML(sourceURL)
		
		# Not an HTML file
		if html == False:
			continue

		print("Scanning %s" % sourceURL)

		for ids in re.finditer('\W(name|id)="(?P<id>.*?)"',html):
			anchorID = ids.groupdict()['id']
			foundAnchors[sourceURL].add(anchorID)

		for link in re.finditer('<a.*?href="(?P<url>.*?)".*?>(?P<text>.*?)</a>',html):
			text = link.groupdict()['text']
			linkURL = link.groupdict()['url']

			if linkURL.startswith('mailto:'):
				continue

			linkURL = urljoin(checkedURLs[sourceURL],linkURL)

			anchor = None
			if '#' in linkURL:
				location = linkURL.index('#')
				anchor = linkURL[(location+1):]
				linkURL = linkURL[:location]
			
			if not linkURL in checkedURLs:
				checkedURLs[linkURL] = checkURL(linkURL)

			links[sourceURL].append( (linkURL, anchor) )
			if linkURL.startswith(filterURL):
				if not linkURL in done and not linkURL in toScan:
					toScan.append(linkURL)

		if args.images:
			for image in re.finditer('<img.*?src="(?P<url>.*?)".*?>',html):
				imageURL = image.groupdict()['url']
				imageURL = urljoin(checkedURLs[sourceURL],imageURL)

				if not imageURL in checkedURLs:
					checkedURLs[imageURL] = checkURL(imageURL)
				links[sourceURL].append( (imageURL, None) )

	output = set()
	for sourceURL in links.keys():
		for linkURL,anchor in links[sourceURL]:
			if anchor is None or not linkURL.startswith(filterURL):
				exists = bool(checkedURLs[linkURL])
				output.add((sourceURL,linkURL,'',exists))
			else:
				exists = anchor in foundAnchors[linkURL]
				output.add((sourceURL,linkURL,'#'+anchor,exists))

	output = [ (checkedURLs[sourceURL],(checkedURLs[linkURL] if checkedURLs[linkURL] else linkURL),anchor,exists) for sourceURL,linkURL,anchor,exists in output ]

	if args.ghpages:
		output = [ (trimRight(sourceURL,'index.html'),trimRight(linkURL,'index.html'),anchor,exists) for sourceURL,linkURL,anchor,exists in output ]
		output = [ (trimRight(sourceURL,'.html'),trimRight(linkURL,'.html'),anchor,exists) for sourceURL,linkURL,anchor,exists in output ]

	output = sorted(list(set(output)))

	with open(args.log,'w') as outF:
		for sourceURL,linkURL,anchor,exists in output:
			if args.all or not exists:
				outF.write("%s\t%s%s\t%s\n" % (sourceURL,linkURL,anchor,str(exists)))

