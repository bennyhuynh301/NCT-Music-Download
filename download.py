import sys
import urllib2
import re
import threading
import Queue

def get_source_url(url):
	is_found = False
	usock = urllib2.urlopen(url)			
	line = usock.readline()
	while line != '':
		if '<div class="player"><div id="flash-player-holder">' in line:
			is_found = True
			break
		line = usock.readline()
	usock.close()
	source_url = '' 	
	if is_found:
		matchObject = re.search(r'<param value="flashid=flash-player&defaultindex=0&autostart=true&file=(.*)" name="flashvars" />', line, re.I)
		if not matchObject:
			matchObject = re.search(r'<param value="flashid=flash-player&defaultindex=0&autostart=true&shuffle=true&file=(.*)" name="flashvars" />', line, re.I)
		source_url = matchObject.group(1)
	return source_url
	
def get_download_urls(source_url):
	download_urls = []
	if source_url	!= '':
		usock = urllib2.urlopen(source_url)
		line = usock.readline()
		usock.close()
		track_lists = line.split('<trackList>')
		for track in track_lists:
			matchObject = re.search(r'<location><!\[CDATA\[(.*)\]\]></location>', track, re.I)
			if matchObject:
				download_urls.append(matchObject.group(1))
	else:
		print "ERROR: Cannot find the source link"
	return download_urls
	
class DownloadThread(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
	
	def run(self):
		while True:
			url = self.queue.get()
			fileName = url.split('/')[-1]
			usock = urllib2.urlopen(url) 
			localFile = open(fileName, 'w')
			print "Downloading :" + fileName
			localFile.write(usock.read())
			usock.close()
			self.queue.task_done()
						
def main(url):
	 	queue = Queue.Queue()
		source_url = get_source_url(url)
		download_urls = get_download_urls(source_url)
		for link in download_urls:
			queue.put(link)
		
		for i in range(10):
			t = DownloadThread(queue)
			t.setDaemon(True)
			t.start()
		
		queue.join()
		print "--------Download Finish--------"
	
if __name__ == '__main__':
	main(sys.argv[1])


	

