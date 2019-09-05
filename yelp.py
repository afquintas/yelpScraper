from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import random
import csv
import re
import time
import sys
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19']

with open('yelp_data.csv', 'w', newline='') as of:
    f = csv.writer(of, delimiter=',')
    f.writerow(["restaurant_title", "restaurant_phoneNumber", "restaurant_address", "restaurant_numReview",
                "restaurant_starCount", "restaurant_price", "restaurant_category", "restaurant_district"])

def extract_data(proxy_pool):
	for i in range(0, 960, 30):
		headers = {"User-Agent": random.choice(user_agents)}
		
		page_html = None
		while page_html is None:
			proxy = next(proxy_pool)
			print('Proxy used: ' + str(proxy))
			try:
				print('teeeeeeeeeeeeees '+ page_html)
				url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc=Porto%2C%20CA&start=' + \
					str(i)	
				page_html = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})
			except:
				print("Connection refused! Test your internet and make sure you have permission to access the site.")
				page_html = None
				pass
			
		headers = {"User-Agent": random.choice(user_agents)}
		bs = soup(page_html.text, "html.parser")

		for item in bs.findAll('div', {"class": "lemon--div__373c0__1mboc largerScrollablePhotos__373c0__3FEIJ arrange__373c0__UHqhV border-color--default__373c0__2oFDT"}):
			restaurant_title = item.h3.get_text(strip=True)
			restaurant_title = re.sub(r'^[\d.\s]+', '', restaurant_title)
			restaurant_phoneNumber = item.select_one(
				'[class*="secondaryAttributes"]').get_text(separator='|', strip=True).split('|')[0]
			restaurant_address = item.select_one(
				'[class*="secondaryAttributes"]').get_text(separator='|', strip=True).split('|')[1]
			restaurant_numReview = item.select_one(
				'[class*="reviewCount"]').get_text(strip=True)
			restaurant_numReview = re.sub(r'[^\d.]', '', restaurant_numReview)
			restaurant_starCount = item.select_one(
				'[class*="stars"]')['aria-label']
			restaurant_starCount = re.sub(r'[^\d.]', '', restaurant_starCount)
			pr = item.select_one('[class*="priceRange"]')
			restaurant_price = pr.get_text(strip=True) if pr else '-'
			restaurant_category = [a.get_text(strip=True) for a in item.select(
				'[class*="priceRange"] ~ span a')]
			restaurant_district = item.select_one(
				'[class*="secondaryAttributes"]').get_text(separator='|', strip=True).split('|')[-1]

			print("Restaurant Name: " + restaurant_title)
			print("Phone Number: " + restaurant_phoneNumber)
			print("Address: " + restaurant_address)
			print("Number of Reviews: " + restaurant_numReview)
			print("Evaluation: " + restaurant_starCount)
			print("Price: " + restaurant_price)
			print("Category: " + ' '.join(restaurant_category))
			print("District: " + restaurant_district)
			print('-' * 80)
			print('\n')
			with open('yelp_data.csv', 'a+', newline='') as of:
				f = csv.writer(of, delimiter=',')
				f.writerow([restaurant_title, restaurant_phoneNumber, restaurant_address, restaurant_numReview,
							restaurant_starCount, restaurant_price, restaurant_category, restaurant_district])

		random_int = random.randint(1, 2)
		time.sleep(random_int)
		
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
	
def main():
	proxies = get_proxies()
	proxy_pool = cycle(proxies)
	extract_data(proxy_pool)
	
if __name__ == '__main__':
    main()
