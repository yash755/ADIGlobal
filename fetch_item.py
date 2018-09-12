import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re
import pymysql.cursors
import os.path


while True:
	try:
		connection = pymysql.connect(host= "108.167.172.175",
			user="dockonef_jashg",
			passwd="gC=wRXPdhUsP",
			db="dockonef_scrape",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor)
		try:
			with connection.cursor() as cursor:
				cursor.execute("SELECT * FROM adi_category")
				connection.commit()

				url = 'https://adiglobal.us/Pages/WebRegistration.aspx'
				driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
				driver.maximize_window()
				driver.get(url)
				time.sleep(2)
				name = driver.find_element_by_name('ctl00$PlaceHolderMain$ctl00$ctlLoginView$MainLoginView$MainLogin$UserName')
				name.send_keys('KASE2046')
				password = driver.find_element_by_name('ctl00$PlaceHolderMain$ctl00$ctlLoginView$MainLoginView$MainLogin$Password')
				password.send_keys('Prodsupp17')
				driver.find_element_by_id("ctl00_PlaceHolderMain_ctl00_ctlLoginView_MainLoginView_MainLogin_LoginButton").click()
				time.sleep(2)
				for row in cursor:
					try:
						data = row
						pageCount = data['id']
						category = data['category']
						pageURL = data['pageurl']
						subCategory = data['subcategory']


						if os.path.isfile('pagecount.txt'):
							file = open('pagecount.txt','r')
							for f in file:
								page = f
						else:
							file = open('pagecount.txt','w')
							file.write(str(pageCount))
							file.close()
							page = pageCount


						if str(page) == str(pageCount):
							
							driver.get(pageURL)
							print ("Fetch data for this category" + subCategory + " & page number is" + page)
							time.sleep(5)
							html2 = driver.page_source
							driver.save_screenshot('test.png')
							soup = BeautifulSoup(html2, "lxml", from_encoding="utf-8")
							members = soup.find_all('li',{'class':'productView'})
							for member in members:
								try:
									image = member.find('div',{'class':'product-image'})
									atag = image.find('a')
									price = member.find('div',{'class':'price'})
									if price:
										price = price.text.strip()
										price = price.replace('\n','')
										price = price.replace('Sale','')
										price = price.replace('Clearance','')
										if atag.get('href') and price:
											print (atag.get('href') + '^^^^^' +  price + '^^^^^' + category + '^^^^^' + subCategory);
											get_item(atag.get('href') + '^^^^^' +  price + '^^^^^' + category + '^^^^^' + subCategory)
								except Exception as e:
									print ("Loop4")
									print (e)
									continue
							
							
							if str(page) == str(cursor.rowcount):
								file = open('pagecount.txt','w')
								file.write(str(1))
								file.close()
							else:
								file = open('pagecount.txt','w')
								file.write(str(pageCount + 1))
								file.close()
						# else:
						# 	print ("No Page Match")

					except Exception as e:
						print ("Loop3")
						print (e)
						continue
		except Exception as e:
			print ('Failed Query')
			print ("Loop2")
			print (e)
	except pymysql.Error as e:
		print ("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
		print ("Loop1")
		time.sleep(2)
		print("Was a nice sleep, now let me continue...")
		


def get_item(parameters):
	try:
		parameters = str(parameters)
		parameters = parameters.split('^^^^^')
		if len(parameters) >= 4:
			if 'Pages' in str(parameters[0]):
				base_url = 'https://adiglobal.us' + str(parameters[0])
				print (base_url)
			else:
				base_url = 'https://adiglobal.us/Pages/' + str(parameters[0])
				print (base_url)
		else:
			print("Sorry")

			final_list = []
			handle = "No Data" #Done
			title = "No Data"  #Done	
			html = "No Data"  #sInfo + SMarketingInfo + sMarketing + Specification
			vendor = "No Data" #Done
			product_type = parameters[3]
			published = "True"
			option1_name = "Title"
			option1_value = "Default Title"
			variant_grams = "No Data"
			variant_inventory_quantity = "1"
			variant_inventory_policy = "deny"
			variant_fulfillment_service = "manual"
			variant_price = "No Data"	#Done
			variant_compare_price = "No Data" #Done
			variant_barcode = "No Data" #Done
			image_src = "No Data" #Done
			image_position = "1"
			gift_card = "False"
			variant_image = "No Data"		#Done
			variant_weight_unit = "lb"

			cat = parameters[2]
			subcat = parameters[3]



			response = requests.get(base_url)
			html = BeautifulSoup(response.content, 'html.parser')
			members = html.find_all('h1')
			if len(members) >=2:
				handle_data = members[1].text.strip()
				handle_data = handle_data.replace(' ','-')
				handle = handle_data
				title = members[1].text.strip()
			
			vendorName = html.find('span',{'class':'vendorName'})
			if vendorName:
				vendor = vendorName.text.strip()


			price = parameters[1]
			price = price.replace('$','')
			price = price.replace('\n','')
			
			variant_price = str(price)
			variant_compare_price = str(price)

		

			imageTag = html.find('div',{'class':'product-img-big'})
			if imageTag:
				imageSrc = imageTag.find('img')
				if imageSrc:
					image_src = str(imageSrc.get('src'))
					variant_image = str(imageSrc.get('src'))


			specsectionmktg_info = html.find('div',{'class':'spec-sectionmktg_info'})
			if specsectionmktg_info:
				sMarketingInfo = specsectionmktg_info.text.strip()
				
				sMarketingInfo = sMarketingInfo.split('Category:')
				if len(sMarketingInfo) >=2:
					sData = sMarketingInfo[1].split('UPC Code:');
					if len(sData) >=2:
						variant_barcode = str(sData[1])

			ProductDetailtab = html.find('div',{'class':'ProductDetailtab-container'})
			if ProductDetailtab:
				html = str(ProductDetailtab)


			driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
			driver.maximize_window()
			driver.get(base_url)
			html2 = driver.page_source
			soup = BeautifulSoup(html2, "lxml", from_encoding="utf-8")
			data_fetch = soup.find('a',{'id':'spectab'})
			if data_fetch:
				driver.find_element_by_xpath('//a[@href="three"]').click()
			time.sleep(2)
			html3 = driver.page_source
			soup = BeautifulSoup(html3, "lxml", from_encoding="utf-8")


			specsectionresults = soup.find('div',{'id':'specsectionresults'})
			if specsectionresults:
				html = html + str(specsectionresults)
				rows = specsectionresults.find_all('div',{'class':'row'})
				for r in rows:
					data_row = r.text.strip()
					if "Weight" in data_row:
						weight_data = data_row
						weight_data = weight_data.split('Weight')
						if len(weight_data) >=2:
							weight = weight_data[1]
							weight = weight.split(' ')
							variant_grams = str(weight[0])
			try:
				connection1 = pymysql.connect(host= "108.167.172.175",
					user="dockonef_jashg",
					passwd="gC=wRXPdhUsP",
					db="dockonef_scrape",
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor)
				try:
					with connection1.cursor() as cursor1:
						cursor1.execute("INSERT INTO adi (handle,title,html,vendor,type,published,option1_name,option1_value,variant_grams,variant_inventory_quantity,variant_inventory_policy,variant_fulfillment_service,variant_price,variant_compare_price,variant_barcode,variant_weight_unit,image_position,gift_card,image_src,variant_image, category, subcategory, productURL) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (handle,title,html,vendor,product_type,published,option1_name,option1_value,variant_grams,variant_inventory_quantity,variant_inventory_policy,variant_fulfillment_service,variant_price,variant_compare_price,variant_barcode,variant_weight_unit,image_position,gift_card,image_src,variant_image,cat,subcat,base_url))
						connection1.commit()
						print ("Inserted")
				except Exception as e:
					print ('Failed Query')
					print (e)
			except pymysql.Error as e:
				print("Connection refused by the server..")
				print ("Loop Internal 2")
				print ("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
				time.sleep(2)
				print("Was a nice sleep, now let me continue...")
			finally:
				connection1.close()														
	except Exception as e:
		print ('Loop Internal 1')
		print (e)											

			
