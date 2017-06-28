from lxml import html
import requests
import os
import sys

# Will download toonova.net toons
# Supply toonova.net page link with tonn episodes listed
#
# Version: 0.2 2017-06-27 22:22
# Author:  hinkocevar@gmail.com
# GIT: https://github.com/hinxx/toonrip

def progress(x):
	mb = float(x)/1e6
	sys.stdout.write("\rgot %0.1f Mb.." % mb)
	sys.stdout.flush()

def pages0(n):
	l = n
	print('trying link:', l)
	page = requests.get(l)
	page
	tree = html.fromstring(page.content)
	ll = tree.xpath('//a')
	pages = 1
	for l in ll:
		# print('link data:', l.attrib)
		if 'href' in l.attrib:
			href = l.attrib['href']
			page = href.find('?page=')
			if page != -1:
				print('page link:', href)
				pages += 1

	print('Have %d of pages total!' % pages)
	return pages

def links0(n, p):
	l = n + '?page=' + str(p)
	print('trying link:', l)
	page = requests.get(l)
	page
	tree = html.fromstring(page.content)
	ll = tree.xpath('//a')
	episodes = []
	for l in ll:
		# print('link data:', l.attrib)
		if 'href' in l.attrib:
			href = l.attrib['href']
			page = href.find('?page=')
			if page != -1:
				continue
			episode = href.find(n)
			if episode != -1:
				print('episode link:', href)
				episodes.append(href)
	return episodes


def links1(l):
	print('trying link:', l)
	page = requests.get(l)
	page
	tree = html.fromstring(page.content)
	ll = tree.xpath('//a')
	vids = []
	for l in ll:
		# print('link data:', l.attrib)
		if 'href' in l.attrib:
			href = l.attrib['href']
			vid = href.find('video=')
			if vid != -1:
				print('page link:', href)
				vids.append(href)
	return vids


def links2(l):
	print('trying link:', l)
	page = requests.get(l)
	page
	tree = html.fromstring(page.content)
	ll = tree.xpath('//a')
	vids = []
	for l in ll:
		# print('link data:', l.attrib)
		if 'href' in l.attrib and 'download' in l.attrib:
			href = l.attrib['href']
			print('video link:', href)
			vids.append(href)
	return vids

def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd, **kwargs)

def single(link, episode):

	print("Looking for episode: %s" % (episode))
	l = "http://www.tubeoffline.com/downloadFrom.php?host=TooNova&video=%s" % link

	f = "%s.mp4" % (episode)
	if os.path.exists(f):
		print("Video already present for episode ", episode)
		return True

	touch(f)

	aa = links1(l)
	#print('all links:', aa)
	print('================================================')
	bb = []
	for a in aa:
		g = links2(a)
		#print("got video link: %s" % g)
		bb = bb + g

	#print('all video links:', bb)
	print('================================================')

	done = False
	for l in bb:
		if done:
			break

		with open(f, 'wb') as handle:
			response = requests.get(l, stream=True)
			print(response)
			sz = 0
			if not response.ok:
				# Something went wrong
				pass
			else:
				for block in response.iter_content(1024):
					handle.write(block)
					sz += len(block)
					progress(sz)

				print("DONE with %s" % f)
				statinfo = os.stat(f)
				if statinfo.st_size > 1024 * 1024:
					done = True


	print("Got file for episode ", episode)
	return True

def main():
	if len(sys.argv) < 2:
		print("Usage %s: uri" % sys.argv[0])
		exit(1)

	n = sys.argv[1]

	pmax = pages0(n)
	for p in range(1,pmax+1):
		print("Fetching episodes for %s" % (n))
		pages = links0(n, p)
		for page in pages:
			link = page
			episode = page.split('/')[-1]
			single(link, episode)


if __name__ == '__main__':
	main()
