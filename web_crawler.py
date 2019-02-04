# import libraries
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import ssl
import urllib.request as request
import html2text
import io

from preprocess import clean_data

def url_check(url):
	"""
	Checks the url if it is accessible.
	It takes into account some possible exceptions.
	"""

	try:
		response = urlopen(url)
		return True
	except urllib.error.HTTPError:
		return False
	except urllib.error.URLError:
		return False
	#except httplib.HTTPException:
	except Exception:
		import traceback
		return False


def get_urls(url):
	"""
	Returns all the urls in the same domain as a list.
	
	"""
	## Get raw html content from url
	content = simple_get(url)

	if content is None:
    	## Try a different protocol
		try:
			context = ssl._create_unverified_context()
			website = urlopen(url, context=context)
			website = urlopen(url)
			content = website.read()
		except:
			url_list = []
			return url_list
    
	soup = BeautifulSoup(content,"html5lib")
	
	links = soup.findAll("a")
	url_list = []
	for link in links:
		sub_url = link.get('href')
		if sub_url is not None:
        	## Check if the url is in the same domain
			if 'http' in sub_url and url_cleaning(url) in sub_url:  
				url_list.append(sub_url)

	print("get_urls done")
	return url_list


def simple_get(url):
    """
    Attempts to get the content at "url" by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
            	return resp.content
            else:
            	return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    if "Content-Type" in resp.headers.keys():
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)


def get_content(url):
	"""
	Converts html content to text, and return the content if it's not None.
	"""
	raw_html = simple_get(url)
	if raw_html is not None:
		try:
			raw_html = str(raw_html.decode("utf-8"))
			text_maker = html2text.HTML2Text()
			text_maker.ignore_links = True
			text_maker.bypass_tables = False
			text_maker.escape_snob = True
			text_maker.ignore_images = True
			text_maker.ignore_anchors = True

			content = text_maker.handle(raw_html)

			return content
		except:
			return None
	else:
		return None


def url_cleaning(website):
	"""
	Removes protocol part from the url, returns the name of the website.
	This is implemented to create "website2mcc" dictionary. In web crawler,
	we only use it to get mcc code for given website from the dictionary.
	Because some websites are written with multiple protocols.
	"""
	website = website.lower()
	website = website.replace("https://", "")
	website = website.replace("http://", "")
	website = website.replace("https://www.", "")
	website = website.replace("http://www.", "")
	website = website.replace("//www.", "")
	website = website.replace("www.", "")
	website = website.replace(" ", "")
	website = website.replace("\xa0", "")

	if website.endswith("/"):
		website = website[:-1]
        
	if website.endswith(")") and website.startswith("("):
		website = website[1:-1]
    
	return website

 	

def read_website2mcc():
	"""
	Reads the MCCs from saved dictionary.
	When we get the web content, we save it with its
	mcc code in the file.
	"""
	website2mcc = {}

	with open("website2mcc") as f:
		lines = f.read().splitlines()
		for line in lines:
			token = line.split(":")
			website2mcc[token[0]] = token[1]

	return website2mcc




def pipeline(website, filename):

	file = open(filename, "w", encoding = "utf-8")
	print("Crawling website: ", website)

	web_name = url_cleaning(website)
	website2mcc = read_website2mcc()
	

	print("url_check: ", url_check(website))
	if url_check(website):
		content = get_content(website)

		if content is not None:
			print("web content is not None")
			content_processed = clean_data(content)
			file.write('%s, %s\n' % (website, content_processed))


		#get url list in the same domain
		urls = get_urls(website)
		print("number of urls: ", len(urls))
		for url in urls:
			if url_check(url):
				content = get_content(url)
				if content is not None:
					content_processed = clean_data(content)
					file.write('%s, %s\n' % (url, content_processed))
					print("preprocessed ", url)

def main():
	# write the website content to the file
	pipeline("https://www.musictabletstore.com/", "filename")
               

if __name__ == '__main__':
	main()