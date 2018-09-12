import requests
from bs4 import BeautifulSoup
import time
import math
import pymysql.cursors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_list():
	try:
		base_url = 'https://adiglobal.us/Company/Pages/Mktg_ShopProducts.aspx?cat=ADI%20US&category=0000&parent=0000'
		print (base_url)
		response = requests.get(base_url)
		html = BeautifulSoup(response.content, 'html.parser')

		dbCategory = ''
		dbSubcategory = ''
		dbPageURL = ''
		dbPageNumber = ''

		u_categories = html.find('ul',{'class':'subCategory'})
		if u_categories:
			categories = u_categories.find_all('li')
			if categories:
				for category in categories:
					dbCategory = str(category.text.strip())
					a = category.find('a')
					try:
						category_url = 'https://adiglobal.us' + a.get('href')
						catResponse = requests.get(category_url)
						cathtml = BeautifulSoup(catResponse.content, 'html.parser')

						u_subcategories = cathtml.find('ul',{'class':'subCategory toplvls'})
						if u_subcategories:
							subcategories = u_subcategories.find_all('li')
							if subcategories:
								for subcategory in subcategories:
									dbSubcategory =  str(subcategory.text.strip())
									sub_a = subcategory.find('a')
									try:
										subcategory_url = 'https://adiglobal.us' + sub_a.get('href')
										driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
										driver.maximize_window()
										driver.get(subcategory_url)
										time.sleep(2)
										
										subCatResponse = driver.page_source
										subcathtml = BeautifulSoup(subCatResponse, "lxml", from_encoding="utf-8")
										
										
										page_no = subcathtml.find('div',{'class':'status'})
										if page_no:
											page = page_no.text.strip()
											page = page.split('of')
											if len(page) >=2:
												page_is = int(page[1])
												pagenumber = math.ceil(page_is/64)
												
												url_param = subcategory_url.split('?')
												if len(url_param) >=2:
													url_is = url_param[1]
													url_is = url_is.replace('c=','')
													url_is = url_is.replace('&m=c','')
													page = 0
													while page <= pagenumber:
														try:
															dbPageURL = 'https://adiglobal.us/Pages/Results.aspx?c=' + str(url_is) + '&p=' + str(url_is) + '&m=c&searchCat=' + str(url_is) + '&pageSize=64&page=' + str(page) + '&dm=g&s=b&rf=&dc='
															
															dbPageNumber = str(page)
															page = page+1
															try:
																connection = pymysql.connect(host= "108.167.172.175",
																	user="dockonef_jashg",
													                passwd="gC=wRXPdhUsP",
													                db="dockonef_scrape",
													                charset='utf8mb4',
												                    cursorclass=pymysql.cursors.DictCursor)
																try:
																	with connection.cursor() as cursor:
																		cursor.execute("INSERT INTO adi_category (category,subcategory,pageurl,pagenumber) VALUES (%s,%s,%s,%s)", (dbCategory,dbSubcategory,dbPageURL,dbPageNumber))
																		connection.commit()
																		print ("Inserted")
																except Exception as e:
																	print ('Failed Query')
																	print (e)
																finally:
																	connection.close()
															except pymysql.Error as e:
																print("Connection refused by the server..")
																print("Let me sleep for 2 seconds")
																print ("Loop5")
																print ("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
																time.sleep(2)
																print("Was a nice sleep, now let me continue...")
																continue															
														except Exception as e:
															print(e)
															print ("Loop4")
															time.sleep(2)
															print("Was a nice sleep, now let me continue...")
															continue													
									except Exception as e:
										print(e)
										print ("Loop3")
										time.sleep(2)
										print("Was a nice sleep, now let me continue...")
										continue
					except Exception as e:
						print(e)
						print("Loop2...")
						time.sleep(2)
						print("Was a nice sleep, now let me continue...")
						continue
	except Exception as e:
		print(e)
		print("Loop1...")
		time.sleep(2)
		print("Was a nice sleep, now let me continue...")
		

if __name__ == '__main__':
	get_list()
