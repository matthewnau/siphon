#!/usr/bin/env python

"""Scrapes and filters news articles, the renders them into html content.

Siphon is a web-scraper that uses a provided url in order to parse html
from different websites. The html is parsed so that only necessary information
passes through the filter, therefore conserving the user's bandwidth. Once the
html is parsed, it is presented in a human-readable, html document.
"""

import sys,urllib,http.cookiejar,gzip                       #Utilize multiple Python modules.
from os import system                                       #Utilize Python's built-in os module.
from datetime import datetime
from bs4 import BeautifulSoup                               #Utilize the BeautifulSoup html parser.
from flask import request,redirect,url_for,render_template  #Utilize the Flask web framework.
from flask import make_response								#Utilize the Flask web framework.
from siphon import app                                      #Utilize the Siphon app for Flask.
from urllib.parse import urlsplit                           #Utilize Python's url splitter module.
from urllib.request import urlopen,build_opener,Request     #Utilize Python's url request module.

"""Detail all the metadata of this program directly below this block.

This explains everyone who was involved with the making of this software.
The credits variable refers to anyone who offered a suggestion that was 
implemented, reported a bug, or was involved in any way without physically
altering any of the source code for this project.
"""

__author__     = "Matthew Nau"
__copyright__  = "Copyright 2016, Matthew David Nau"
__credits__    = ["Matthew Nau"]

__license__    = "None"
__version__    = "4.5.0"
__language__   = "Python 3.5.2 (32-bit)"
__maintainer__ = "Matthew Nau"
__email__      = ""
__status__     = "Development"

def get_html():
	global html,page,address
	address.append(url)
	req = Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'})
	html = urlopen(req).read()
	if(str(type(html))=="<class 'bytes'>")and(('<!DOCTYPE'not in html.decode('utf-8','backslashreplace'))and('<!doctype'not in html.decode('utf-8','backslashreplace'))):
		html = str(gzip.decompress(html),'utf-8')
	page = BeautifulSoup(html,"html.parser")

def make_html():
	global file
	global title
	title = page.find('title').text.strip()

@app.route('/')
def index():
	return render_template('index.html',title='Siphon')

@app.route('/humans.txt')
def humans():
	return render_template('humans.txt')

@app.route('/share/<path:shortcut>')
def share(shortcut):
	response = make_response(redirect('/',code=307))
	response.set_cookie('siphon_cookie_url',value=shortcut)
	return response

@app.route('/', methods=['POST'])
def get_data():
	global url,html,page,file,publisher,domain,address,title
	url = str(request.form['searchbox'])
	file = []
	address = []
	if 'https://www.google.com/url?' in url:
		url_cookie_jar = http.cookiejar.CookieJar()
		url_cookie_html = build_opener(urllib.request.HTTPCookieProcessor(url_cookie_jar)).open(url)
		url_cookie_page = str(BeautifulSoup(url_cookie_html,'html.parser'))
		url = url_cookie_page[url_cookie_page.index('"htt')+1:url_cookie_page.index('");\n')]

	if ('http:/' in url) or ('https:/' in url):
		url = url
	else:
		url = 'http:/'+url
	originalUrl = url
	domain = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
	publisher = domain
	if publisher.count('.') < 2:
		publisher = publisher[:publisher.index('://')+3]+'www.'+publisher[publisher.index('://')+3:]
	publisher = publisher[publisher.index('.')+1:len(publisher)-(publisher[::-1].index('.')+1)]
	publisher = publisher[0].upper()+publisher[1:].lower()

	if 'www.mediaite.com' in url:                                       #If the webpage being scraped is from 'www.mediaite.com,'
		get_html()                                                      #Retrieve the necessary html from the webpage.
		make_html()                                                     #Begin writing html to the external file.
		article = page.find("div", {"id":"post-body"}).find_all('p')    #Make a list of all 'p' elements found in a div with the id of 'post-body.'
		for p_element in article:                                       #Repeat the following steps for every item in the article list,
			file.append('<p>'+p_element.text+'</p>\n')                  #Write the text from the 'p' element to the newly made html file from above. Write it in between 'p' tags, then go to the next line.

	elif 'www.washingtonpost.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"id":"article-body"}).find_all('p')
		for p_element in article:
			if 'class="interstitial-link"' not in str(p_element):
				if 'class="trailer"' not in str(p_element):
					file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.nbcnews.com' in url:
		get_html()
		make_html()
		if not bool(page.find("div", {"class":"article-body"})):
			article = "This was a video. Sorry"
		else:
			article = page.find("div", {"class":"article-body"}).find_all('p')
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'abcnews.go.com' in url: #[COMPLETE]
		get_html()
		make_html()
		article = page.find("div", {"class":"article-copy"}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.npr.org' in url:
		get_html()
		make_html()
		article = page.find("div", {"id":"storytext"}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.nydailynews.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('article',{'class':'g-article'}).find_all('p',{'itemprop':'articleBody'})
		else:
			article = page.find("article", {"id":"ra-body"}).find_all('p',recursive=False)
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.yahoo.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('article',{'class':'article'}).find_all('p')
		else:
			article = page.find("div", {"class":"canvas-body"}).find_all('p',recursive=False)
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.wsj.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			if ('http:/' in url) or ('https:/' in url):
				url = url
			else:
				url = 'http:'+url #this url shit might be neceessary if some amp urls are unreconizable for other sites.
			get_html()
			if bool(page.find("div", {"amp-access":"access OR meterCount < meterLimit"})):
				article = page.find('div',{'amp-access':'access OR meterCount < meterLimit'}).find_all('p')
			else:
				article = page.find('div',{'class':'articleBody'}).find('div',{'class':''}).find_all('p')
		else:
			article = page.find("article", {"id":"ra-body"}).find_all('p',recursive=False)#broke af, not done
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.businessinsider.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('section',{'class':'article-content'}).find_all('p',recursive=True)
		else:
			article = page.find("div", {"class":"KonaBody post-content"}).find_all('p',recursive=True)
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.theverge.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('div',{'class':'article__body'}).find_all('p',recursive=True)
		else:
			article = page.find("div", {"class":"m-article__entry"}).find_all('p',recursive=False)
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.cnet.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('div',{'id':'article-main-body'}).find_all('p')
		else:
			article = page.find("div", {"class":"col-8"}).find_all('p',recursive=False)
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.people.com' in url: #wip
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('div',{'class':'article'})
		else:
			article = page.find("div", {"id":"articleBody"})
		make_html()
		file.append('<p>'+article.text+'</p>\n')

	elif '.chicagotribune.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('div',{'itemprop':'articleBody'}).find_all('p')
		else:
			article = page.find("div", {"itemprop":"articleBody"}).find_all('p')
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.huffingtonpost.com' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find("div",{"class":"entry__body js-entry-body"}).find_all('p')
		else:
			article = page.find("div",{"class":"entry__body js-entry-body"}).find_all('p')
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.pcworld.com' in url:
		get_html()
		make_html()
		article = page.find("section", {"class":"page"}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'abc30.com' in url:    
		get_html()
		make_html()
		article = str(page.find("div", {"class":"body-text"})).split('<br>')
		paragraphs = []
		paragraphs.append(article[0])
		for paragraph in article:
			if (not (('<div' in paragraph) or ('</div>' in paragraph) or ('<br>' in paragraph) or ('</br>' in paragraph) or (paragraph == ''))):
				paragraphs.append(paragraph)
		paragraphs.append(article[len(article)-1])
		paragraphs[len(paragraphs)-1] = ((paragraphs[len(paragraphs)-1][::-1])[(paragraphs[len(paragraphs)-1][::-1]).index('.'):])[::-1]
		if 'dateline' in paragraphs[0]:
			paragraphs.insert(0,paragraphs[0][paragraphs[0].index('dateline">')+10:paragraphs[0].index('</div>')])
			paragraphs[1] = (paragraphs[1][paragraphs[1].index('</div>')+6:]).lstrip()
			paragraphs[1] = paragraphs[0] + ' ' + paragraphs[1]
			paragraphs.remove(paragraphs[0])
			new_html = ''
			for paragraph in paragraphs:
				new_html += ('<p>'+paragraph+'</p>\n')
			new_page = BeautifulSoup(new_html,"html.parser")
			article = new_page.find_all('p')
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')
		else:
			new_html = ''
			for paragraph in paragraphs:
				new_html += ('<p>'+paragraph+'</p>\n')
			new_page = BeautifulSoup(new_html,"html.parser")
			article = new_page.find_all('p')
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.recode.net' in url:
		get_html()
		make_html()
		article = page.find('div', {'class':'c-entry-content'}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.chron.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"article-body"}).find_all('p',recursive=False)
		for p_element in article:
			if ((not bool(p_element.find('a'))) or (not bool(p_element.find('strong')))):
				if not bool(p_element.find('em')):
					file.append("<p>"+p_element.text+"<p>\n")

	elif 'www.techtimes.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"at-body"}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'ihatetomatoes.net' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"entry-content"}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.bbc.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"story-body__inner"}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.theguardian.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"content__article-body from-content-api js-article__body"}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.thedailybeast.com' in url:
		get_html()
		make_html()
		article = page.find("div", {"class":"BodyNodes"}).find_all("div", {"class":"Text"})
		for div_element in article:
			file.append('<p>'+div_element.text+'</p>\n')

	elif 'www.bostonglobe.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'article-text'}).find_all('p',recursive=False)
		for p_element in article:
			if not bool(p_element.find('style')):
				if not bool(p_element.find('b')):
					file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.usatoday.com' in url:
		get_html()
		make_html()
		if '.com/videos/' in url:
			file.append('<p>Sorry. This is a video. We do not support this media.</p>\n')
		else:
			article = page.find('div',{'itemprop':'articleBody'}).find_all('p',recursive=False)
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.foxnews.com' in url:
		get_html()
		make_html()
		if bool(page.find('div',{'class':'article-text'})):
			article = page.find('div',{'class':'article-text'}).find_all('p',recursive=False)
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')
		else:
			article = page.find('div',{'itemprop':'articleBody'}).find_all('p',recursive=False)
			for p_element in article:
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.foxsports.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'flex-article-content content-body story-body'}).find_all('p')
		for p_element in article:
			if (article.index(p_element) % 2 == 0) or (article.index(p_element) == 0):
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.latimes.com' in url: #[COMPLETE]
		get_html()
		make_html()
		article = page.find('div',{'itemprop':'articleBody'}).find_all('div',{'class':'trb_ar_page'})
		for div_element in article:
			if len(div_element.find_all('li')) > len(div_element.find_all('p')):
				paragraphs = div_element.find_all('li')
				for li_element in paragraphs:
					file.append('<p>'+li_element.text+'</p>\n')
			paragraphs = div_element.find_all('p')
			for p_element in paragraphs:
				if not bool(p_element.find('strong')):
					file.append('<p>'+p_element.text+'</p>\n')
					
	elif ".cnn.com" in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			make_html()
			article = page.find('div',{'class':'body_text'}).find_all('p')
		elif 'money.cnn.com' in url:
			make_html()
			article = page.find('div',{'id':'storytext'}).find_all('p')
		else:
			article = page.find('div',{'class':'el__leafmedia el__leafmedia--sourced-paragraph'})
			make_html()
			file.append('<p>'+article.text+'</p>\n')
			article = page.find_all('div',{'class':'zn-body__paragraph'})
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.thedailybeast' in url:
		get_html()
		make_html()
		article = page.find_all('div',{'class':'wrapper text'})
		for div_element in article:
			file.append('<p>'+div_element.find('p').text+'</p>\n')

	elif 'www.nytimes.com' in url: #[COMPLETE]
		address.append(url)
		cookie_jar = http.cookiejar.CookieJar()
		cookie_html = build_opener(urllib.request.HTTPCookieProcessor(cookie_jar)).open(url).read()
		cookie_page = BeautifulSoup(cookie_html,'html.parser')
		title = cookie_page.find('title').text.strip()
		article = cookie_page.find_all('p',{'class':'story-body-text story-content'})
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.inc.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'article-body inc_editable'}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.reuters.com' in url:
		get_html()
		make_html()
		article = page.find('span',{'id':'article-text'}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'cbslocal.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'story'}).find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.politico.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'story-text'}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'www.nfl.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'articleText'}).find_all('p')
		for p_element in article:
			if not bool(p_element.find('script')):
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'nbcsports.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'entry-content'}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'mashable.com' in url:
		get_html()
		make_html()
		article = page.find('section',{'class':'article-content'}).find_all('p',recursive=False)
		for p_element in article:
			if 'Have something to add to this story? Share it in the comments.' not in p_element.text:
				file.append('<p>'+p_element.text+'</p>\n')

	elif 'kotaku.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'post-content entry-content js_entry-content '}).find_all('p')
		for p_element in article:
			if not bool(p_element.find('small',{'class':'proxima'})):
				file.append('<p>'+p_element.text+'</p>\n')

	elif '.forbes.com/sites' in url:
		get_html()
		if 'rel="amphtml"' in str(html):
			url = page.find('link',{'rel':'amphtml'}).get('href')
			get_html()
			article = page.find('div',{'class':'article-header inner-contain'}).find_all('p')
		else:
			article = page.find("div", {"class":"article-injected-body"}).find_all('p')
		make_html()
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'forbes.com' in url:
		get_html()
		make_html()
		forbes_url = url+'amp'
		forbes_html = urlopen(forbes_url).read()
		forbes_page = BeautifulSoup(forbes_html,"html.parser")
		forbes_title = url[::-1][url[::-1].index('/')+1:][:url[::-1][url[::-1].index('/')+1:].index('/')][::-1].replace('-',' ')
		forbes_title = forbes_title[0].upper()+forbes_title[1:].lower()
		file.append(file[0][:file[0].index('id="header-title">')+18]+forbes_title+'</h1><hr>\n')
		file.remove(file[0])
		article = forbes_page.find('div',{'class':'article-body inner-contain'}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif '.freep.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'itemprop':'articleBody'}).find_all('p',recursive=False)
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	elif 'bizjournals.com' in url:
		get_html()
		make_html()
		article = page.find('div',{'class':'content'}).find_all('p',{'class':'content__segment'})
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')

	else:
		get_html()
		make_html()
		article = page.find_all('p')
		for p_element in article:
			file.append('<p>'+p_element.text+'</p>\n')
			
	file = ''.join(file)
	share_url = "https://www.siphon.news/share/"+originalUrl
	mla_citation = '"'+title+"."+'" '+publisher+'. N.p., n.d. Web. '+str(datetime.today().day)+" "+datetime.now().strftime("%B")[0:3]+'. '+datetime.now().strftime("%Y")+'. <'+originalUrl+'>.'
	return render_template('article.html',title=title,file=file,url=originalUrl,share_url=share_url,mla=mla_citation)

@app.errorhandler(500)
def error_500(e):
	return 'Something went wrong. Error 500.'

@app.errorhandler(404)
def error_404(e):
	return 'Something went wrong. Error 404.'