from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import threading
import os
from os import path
from os import getcwd
from os import mkdir
from os.path import exists as isexist
import pandas as pd
from dclass import respath, remoteread_file, pprint, Db
from time import sleep
import webbrowser
import sys


driverpath = path.join(getcwd(), "driver")
if not isexist(driverpath): mkdir(driverpath)

class Scrapp():
    #urlBase https://konga.com
    #previewContainerclass = '_06822_e7mpG'
    #waitID = "mainContent"
    #waitCLASS = "maincontent"
    def __init__(self,sitename, urlBase, waitID, waitCLASS, previewContainerclass):
        self.limit = 0
        self.waitID = waitID
        self.waitCLASS = waitCLASS
        self.previewContainerclass = previewContainerclass
        self.url = urlBase
        urlName = sitename
        self.internal = urlName
        self.category = []
        self.pages = []
        self.extractingdetails = 0
        self.extractingpage = 0
        self.dbname = urlName + '.db'
        self.db = Db(respath(self.dbname))
        self.createDB()
        self.notallow = ['#', 'twitter','facebook','youtube','google','instagram']

    def browserdriver(self):
        try:
            return ChromeDriverManager(path=driverpath).install()
        except:
            print("Error downloading driver")
            return False
    
            
    def createDB(self):
            #db = Db(respath(self.dbname))
            create_dcategory_table = """ CREATE TABLE IF NOT EXISTS dcategory (
                        id integer PRIMARY KEY,
                        url MEDIUMTEXT NOT NULL,
                        status INTEGER
                    ); """

            create_dpages_table = """ CREATE TABLE IF NOT EXISTS dpages (
                                id integer PRIMARY KEY,
                                url MEDIUMTEXT NOT NULL,
                                status INTEGER
                            ); """
                            
            create_ddata_table = """ CREATE TABLE IF NOT EXISTS ddata (
                                        id integer PRIMARY KEY,
                                        dpageid INTEGER,
                                        brandname text NOT NULL, 
                                        main_category text NOT NULL, 
                                        sub_categories text NOT NULL, 
                                        title text NOT NULL, 
                                        images text NOT NULL, 
                                        price text NOT NULL, 
                                        selling_price text NOT NULL, 
                                        discount text NOT NULL, 
                                        description blob, 
                                        product_code text NOT NULL, 
                                        review text NOT NULL, 
                                        link MEDIUMTEXT NOT NULL
                                    ); """
            
            self.db.createdb(create_dcategory_table)
            self.db.createdb(create_dpages_table)
            self.db.createdb(create_ddata_table)
            
    def run(self):
        step2 = input(f"Welcome to {self.internal} scrapper enjoy\n\nDo you want to start scrapping now? (y/n):  ").lower()
        if step2 == 'y':
            checkdb2 = self.db.check('id', 'dcategory', f"id!='' ")
            if checkdb2:
                step = int(input("You have some unfinished processing. Select options to continue\n\n1. Continue Extract pages and Extract Details\n2. Export saved Details only\n3. Export saved Details and continue extracting\n4. Extract Details only\n5. Start new session\n6. Clear all session and exits : "))
                if step ==1:
                    self.extractPages()
                elif step ==2:
                    self.saveData()
                elif step ==3:
                    self.extractPages()
                    self.saveData()
                elif step ==4:
                    self.extractDetails()
                elif step ==5:
                    self.db.others(f"DELETE FROM dcategory")
                    self.db.others(f"DELETE FROM dpages")
                    self.db.others(f"DELETE FROM ddata")
                    self.dosubProcess()
                elif step ==6:
                    self.db.others(f"DELETE FROM dcategory")
                    self.db.others(f"DELETE FROM dpages")
                    self.db.others(f"DELETE FROM ddata")
                    sys.exit()
                else:
                    print("Sorry no option was select try again")
                    self.run()
            else:
                self.dosubProcess()
        else:
            sys.exit()
    
    def notallowit(self, url):
        for pasre in self.notallow:
            if pasre in url: return True
        return False
    
    def dosubProcess(self):
        print("Connecting to "+ str(self.internal))
        
        try:
            options = Options()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--test-type")
            options.add_argument("--headless")
            browser = webdriver.Chrome(executable_path=self.browserdriver(), options=options)
            #try parsing with selenium
            browser.get(self.url)
            #wait for the browser page to load
            waitToLoad = WebDriverWait(browser, 5)
            #wait until the target class is loaded and found
            if self.waitCLASS:
                waitToLoad.until(EC.presence_of_element_located((By.CLASS_NAME, self.waitCLASS)))
                #if successfully loaded store it to pagecontents variable
                allcategories_link = browser.find_element_by_class_name(self.waitCLASS)
            else:
                waitToLoad.until(EC.presence_of_element_located((By.ID, self.waitID)))
                #if successfully loaded store it to pagecontents variable
                allcategories_link = browser.find_element_by_id(self.waitID)
                
            dcontent = allcategories_link.get_attribute("outerHTML")
            
            browser.quit()
        except:
            #try process with get
            dcontent = remoteread_file(self.url)
        
        
        try:
            content = bs(dcontent, 'html.parser')
            
            for totalfound_href in content.find_all('a'):
                try:
                    foundurl = totalfound_href["href"]
        
                    if not foundurl.startswith('http') or not foundurl.startswith('https'):
                        foundurl = self.url+'/'+ foundurl.lstrip('/')
                    
                    if self.internal == "jumia":                    
                        if not ".html" in foundurl and not self.notallowit(foundurl) and self.internal in foundurl:
                            checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                            if checkdb is None:
                                print("Category saved ", foundurl)
                                self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                                
                    else:
                        if "category" in foundurl and not self.notallowit(foundurl) and self.internal in foundurl:
                            checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                            if checkdb is None:
                                print("Category saved ", foundurl)
                                self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                            
                except Exception as e:
                    print("Category page error ", e)
            
        except Exception as e:
            print('sub category error: '+ str(e))
        
        '''
        p1 = threading.Thread(name='Process Category', target=self.extractPages)
        p1.start()
        p2 = threading.Thread(name='Process Category', target=self.extractDetails)
        p2.start()
        '''
        self.extractPages()
    
    def extractPages(self):
        
        while True:
            getPages = self.db.fetch(f"SELECT * FROM dcategory WHERE status='0' ORDER BY id DESC ")
            if len(getPages):
                page = ''
                for pag in getPages:
                    page = pag['url']
                    print("Processing Category", page)
                    options = Options()
                    options.add_argument('--ignore-certificate-errors')
                    options.add_argument("--test-type")
                    options.add_argument("--headless")
                    
                    try:
                        browser = webdriver.Chrome(executable_path=self.browserdriver(), options=options)
                        #try parsing with selenium
                        browser.get(page)
                        #wait for the browser page to load
                        waitToLoad = WebDriverWait(browser, 5)
                        #wait until the target class is loaded and found
                        if self.waitCLASS:
                            waitToLoad.until(EC.presence_of_element_located((By.CLASS_NAME, self.waitCLASS)))
                        else:
                            waitToLoad.until(EC.presence_of_element_located((By.ID, self.waitID)))
                        #if successfully loaded store it to pagecontents variable
                        allcategories_link = browser.find_element_by_class_name(self.previewContainerClass)
                        dcontent = allcategories_link.get_attribute("outerHTML")
                        
                        browser.quit()
                    except:
                        #try process with get
                        dcontent = remoteread_file(page)

                    try:
                        content = bs(dcontent, 'html.parser')
                        
                        for totalfound_href in content.find_all('a'):
                            try:
                                foundurl = totalfound_href["href"]
                                if foundurl:
                                    if not foundurl.startswith('http') or not foundurl.startswith('https'):
                                        foundurl = self.url+'/'+ foundurl.lstrip('/')
                                        
                                                        
                                    if self.internal == "jumia":   
                                        if ".html" in foundurl and self.internal in foundurl:     
                                            checkdb = self.db.check('id', 'dpages', f"url='{foundurl}' ")
                                            if checkdb is None:
                                                print("Page saved ", foundurl)
                                                self.db.insert('dpages', 'url, status', f"'{foundurl}', '0' ")
                                                                         
                                        else:
                                            if not self.notallowit(foundurl) and self.internal in foundurl:
                                                checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                                                if checkdb is None:
                                                    print("Category saved ", foundurl)
                                                    self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                                                
                                    else:
                                        if "category" in foundurl and self.internal in foundurl and not "=" in foundurl:                     
                                            if not self.notallowit(foundurl):          
                                                checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                                                if checkdb is None:
                                                    print("Category saved ", foundurl)
                                                    self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                                        else:
                                            if "product" in foundurl and self.internal in foundurl and not "=" in foundurl:
                                                checkdb = self.db.check('id', 'dpages', f"url='{foundurl}' ")
                                                if checkdb is None:
                                                    print("Page saved ", foundurl)
                                                    self.db.insert('dpages', 'url, status', f"'{foundurl}', '0' ")
                            except Exception as e:
                                print("Page error ", e)
                                
                    except Exception as e:
                        print('pages or category error: '+ str(e))
                        
                    self.db.others(f"UPDATE dcategory SET status=1 WHERE id='{pag['id']}'")
                    sleep(1)
                    
            else:
                self.extractDetails()
                break
                        
    
    def extractDetails(self):
        countfound = 0
        #getPage = ['https://www.jumia.com.ng/sony-ps4-efootball-pro-evolution-soccer-pes-2020-40897803.html', 'https://www.jumia.com.ng/gerber-babies-wash-clothes-8-piece-gerber-mpg281849.html','https://www.jumia.com.ng/generic-baby-towel-gift-sets-3-in-1-43597455.html']
        #getPage =[r'C:\PythonProjects\myProject\PendingProject\konga-jiji-spar-jumia\jumia_sunny2.htm']
        
        while True:
            if self.limit:
                if self.limit >= countfound:
                    self.extractingdetails = 0
                    break
    
            getPage = self.db.fetch(f"SELECT * FROM dpages WHERE status='0' ORDER BY id ASC ")
            if len(getPage):
                print("Extracting Details begins...")
                page = ''
                for pag in getPage:
                    page = pag['url']
                    #page = pag
                    countfound +=1
                    if self.limit:
                        if self.limit >= countfound:
                            self.extractingdetails = 0
                            break
                        
                    print("Extraction begins on page", page)
                    
                    try:
                        opts = Options()
                        opts.add_argument('--ignore-certificate-errors')
                        opts.add_argument("--test-type")
                        opts.add_argument("--headless")
                        browser = webdriver.Chrome(executable_path=self.browserdriver(), options=opts)
                        #try parsing with selenium
                        browser.get(page)
                        #wait for the browser page to load
                        waitToLoad = WebDriverWait(browser, 5)
                        #wait until the target class is loaded and found
                        if self.waitCLASS:
                            waitToLoad.until(EC.presence_of_element_located((By.CLASS_NAME, self.waitCLASS)))
                            #if successfully loaded store it to pagecontents variable
                            allcategories_link = browser.find_element_by_class_name(self.waitCLASS)
                        else:
                            waitToLoad.until(EC.presence_of_element_located((By.ID, self.waitID)))
                            #if successfully loaded store it to pagecontents variable
                            allcategories_link = browser.find_element_by_id(self.waitID)    
                            
                        dcontent = allcategories_link.get_attribute("outerHTML")
                        
                        browser.quit()
                    except:
                        #try process with get
                        dcontent = remoteread_file(page) 
                    '''
                    with open(page, 'rb') as ty:
                        dcontent = ty.read()
                    '''
                        
                    try:  
                        content = bs(dcontent, 'html.parser')
                        
                        for totalfound_href in content.find_all('a'):
                            try:
                                foundurl = totalfound_href["href"]
                                if foundurl:
                                    if not foundurl.startswith('http') or not foundurl.startswith('https'):
                                        foundurl = self.url+'/'+ foundurl.lstrip('/')
                                        
                                    if self.internal == "jumia":   
                                        if ".html" in foundurl and self.internal in foundurl:        
                                            checkdb = self.db.check('id', 'dpages', f"url='{foundurl}' ")
                                            if checkdb is None:
                                                print("Page saved ", foundurl)
                                                self.db.insert('dpages', 'url, status', f"'{foundurl}', '0' ")
                                                                        
                                        else:
                                            if not self.notallowit(foundurl) and self.internal in foundurl:
                                                checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                                                if checkdb is None:
                                                    print("Category saved ", foundurl)
                                                    self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                                                
                                    else:
                                        if "category" in foundurl and self.internal in foundurl and not self.notallowit(foundurl):                               
                                            checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                                            if checkdb is None:
                                                print("Category saved ", foundurl)
                                                self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                                        else:
                                            if "product" in foundurl and self.internal in foundurl and not self.notallowit(foundurl):
                                                checkdb = self.db.check('id', 'dpages', f"url='{foundurl}' ")
                                                if checkdb is None:
                                                    print("Page saved ", foundurl)
                                                    self.db.insert('dpages', 'url, status', f"'{foundurl}', '0' ")
                            except:
                                pass
                        
                        if self.internal == "konga":
                            maindiv = content.find(class_="d9549_IlL3h")
                            
                            try:
                                maindiv2 = maindiv.find(class_="_31c33_NSdat")
                                resultspan = maindiv2.find_all("span")
                                if len(resultspan) > 2:
                                    resultReview = maindiv2.find_all("span")[0].getText()
                                    resultProductCode = maindiv2.find_all("span")[1].getText()
                                else:
                                    resultReview = 0
                                    resultProductCode = maindiv2.find_all("span")[0].getText()
                            except Exception as e:
                                resultReview = 0
                                resultProductCode = 0
                                
                            try:
                                resultTitle = maindiv.find("h4").getText()
                            except:
                                resultTitle = ''
                                
                            try:
                                resultBrand = maindiv.find("h5").getText()
                            except:
                                resultBrand = ''
                                
                            try:
                                maindiv3 = maindiv.find_all(class_="_3924b_1USC3")[2]
                                allprice = maindiv3.find_all("div")
                                resultPricediscount = allprice[1].getText().replace("?", '')
                                resultPrice = allprice[2].getText().replace("?", '')
                                resultPricesaved = allprice[3].find("span").getText().replace("You save", "").replace("?", '').strip('')
                                
                            except:
                                resultPrice = 0
                                resultPricediscount = 0
                                resultPricesaved = 0
                            
                            resultImage = ''
                            try:
                                maindiv5 = maindiv.find(class_="bf1a2_3kz7s")
                                for img in maindiv5.find_all("img"):
                                    resultImage += img["src"] + '\n'
                            except:
                                pass
                                
                            
                            try:
                                resultAllsubcate = ''
                                maindiv6 = content.find(class_="f9286_1HlF_")
                                resultMainsubcate = maindiv6.find("h1").getText()
                                for subcat in maindiv6.find_all("li"):
                                    resultAllsubcate += subcat.getText()+ ' > '
                            except:
                                resultAllsubcate = ''
                                resultMainsubcate = ''
                            
                            try:
                                maindiv4 = maindiv.find(class_="_227af_AT9tO")
                                #tabs = maindiv4.find(class_="_8ed9d_3tJB8")
                                #for dotab in tabs.find_all("a"):
                                #    #allo selenium to click on all the a hreg tags and get the results 
                                #    tabname = dotab.find("h3").getText()
                                #    dotabname = browser.dotab.click()
                                #    print("Tabname", tabname)
                                #    tabcontent = maindiv4.find(class_="_3383f_1xAuk")
                                #    print(str(tabcontent))
                                resultDescription = maindiv4.find(class_="_3383f_1xAuk")
                            except:
                                resultDescription = ''
                            
                            resultImage = resultImage.rstrip('\n')
                            resultAllsubcate = resultAllsubcate.rstrip(" > ")
                            if resultTitle:
                                checkdb = self.db.check('id', 'ddata', f"dpageid='{pag['id']}' ")
                                if checkdb is None:
                                    print("\n\nData saved ", str(resultTitle),'\n\n')

                                    self.db.insert2("""INSERT INTO ddata (dpageid,brandname,main_category, sub_categories,title,images,price,selling_price,discount,description,product_code,review, link) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);""", (pag['id'],resultBrand, resultMainsubcate,resultAllsubcate,resultTitle,resultImage,resultPrice,resultPricediscount,resultPricesaved,resultDescription.encode(),resultProductCode, resultReview, page))
                                    
                                    
                        elif self.internal == "jumia":
                            #jumia process
                            maindiv = content
                                
                            try:
                                resultTitle = maindiv.find("h1").getText()
                            except:
                                resultTitle = ''
                            
                            #get brand name 
                            try:
                                resultBrand = maindiv.find("div", class_ ="-fs14 -pvxs").find_all('a')[0].getText()
                            except Exception:
                                resultBrand = ''
                            
                            #get review
                            try:
                                resultReview = maindiv.find("div", class_ ="-df -i-ctr -pvxs").find_all('a')[0].getText().replace("(", "").replace(")", "")
                            except:
                                resultReview = 0
                                
                            #get prices and discount
                            maindiv5 = maindiv.find("div", class_="-hr -pvs -mtxs")
                            try:
                                resultPrice = maindiv5.find(class_="-tal -gy5 -lthr -fs16").getText().replace("?", '')
                                resultPricediscount = maindiv5.find(class_="-b -ltr -tal -fs24").getText().replace("?", '')
                                resultPricesaved = 0
                                
                            except Exception as e:
                                print("Price error ", e)
                                resultPrice = 0
                                resultPricediscount = 0
                                resultPricesaved = 0
                            
                            resultImage = ''
                            try:
                                maindiv5 = maindiv.find(class_="-ptxs -pbs")
                                for img in maindiv5.find_all("img"):
                                    resultImage += img["data-src"] + '\n'
                            except:
                                pass
                                
                            try:
                                resultAllsubcate = ''
                                maindiv6 = content.find(class_="brcbs col16 -pts -pbm")
                                resultMainsubcate = maindiv6.find("a").getText()
                                for subcat in maindiv6.find_all("a"):
                                    resultAllsubcate += subcat.getText()+ ' > '
                            except:
                                resultAllsubcate = ''
                                resultMainsubcate = ''
                            
                            #get product sku
                            maindiv4 = maindiv.find_all("div", class_="col12")[0]
                            try:
                                resultProductCode = maindiv4.find("ul", class_="-pvs -mvxs -phm -lsn").find_all("li")[0].getText()
                            except Exception as e:
                                print('code is error', e)
                                resultProductCode = ''
                                
                            try:
                                maindivSpec = str(maindiv4.find("section", class_="card aim -mtm -fs16"))
                                divDescription = str(maindiv4.find("div", class_="card aim -mtm"))
                                
                                resultDescription = str(divDescription + maindivSpec)
                            except Exception:
                                resultDescription = ''
                                
                            resultImage = resultImage.rstrip('\n')
                            resultAllsubcate = resultAllsubcate.rstrip(" > ")
                            
                            pro =f'\n\nbrandname: {resultBrand}\nmain_category: {resultMainsubcate}\nsub_categories: {resultAllsubcate}\ntitle: {resultTitle}\nimages: {resultImage}\nprice: {resultPrice}\nselling_price: {resultPricediscount}\ndiscount: {resultPricesaved}\ndescription: {resultDescription.encode()}\nproduct_code: {resultProductCode}\nreview: {resultReview}'
                            #print(pro)
                            
                            if resultTitle:
                                checkdb = self.db.check('id', 'ddata', f"dpageid='{pag['id']}' ")
                                if checkdb is None:
                                    print("\n\nData saved ", str(resultTitle),'\n\n')

                                    self.db.insert2("""INSERT INTO ddata (dpageid,brandname,main_category, sub_categories,title,images,price,selling_price,discount,description,product_code,review, link) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);""", (pag['id'],resultBrand, resultMainsubcate,resultAllsubcate,resultTitle,resultImage,resultPrice,resultPricediscount,resultPricesaved,resultDescription.encode(),resultProductCode, resultReview, page))
                            
                            
                        print("Finished extracting ", page)
                
                    except Exception as e:
                        print('Error occurred '+ str(e))
                    
                    self.db.others(f"UPDATE dpages SET status=1 WHERE id='{pag['id']}'" )

            else:
                print('Almost done')
                self.saveData()
                break
            
                                         
    def saveData(self): 
        data = {}
        step = int(input("To export please Select options to continue\n\n1. Export Pages only\n2. Export Categories Links Only\n3. Export Extracted Details Only\n4. Exists : "))
        
        if step ==1:
            #Export Pages only
            xls = pd.DataFrame(columns=['Url', 'Processed'])
            
            getData = self.db.fetch(f"SELECT * FROM dpages ORDER BY id ASC ")
            if len(getData):
        
                print("Saving Datas to exceel sheet")
                for result in getData:
                    if result['status']: 
                        mainstatus = "Yes" 
                    else:
                        mainstatus = "No"
                        
                    data['Url'] = result['url']
                    data['ProProcessedcess'] = mainstatus
                    xls = xls.append(data, ignore_index=True)
                    xls.index += 1
                #now save the files
                #save as excel
                try:
                    filesaveName = self.internal.upper() + "_Pages.xlsx"
                    xls.to_excel(filesaveName)
                    webbrowser.open(getcwd())
                    savepath  = path.join(getcwd(), filesaveName)
                    print("Saved successfully to ", savepath)
                except Exception as e:
                    print("Error can not save ", e)
            else:
                print("No Extracted Pages data to save")
            self.saveData()
                
        elif step ==2:
            #Export Categories Links Only
            xls = pd.DataFrame(columns=['Url', 'Processed'])
            
            getData = self.db.fetch(f"SELECT * FROM dcategory ORDER BY id ASC ")
            if len(getData):
        
                print("Saving Datas to exceel sheet")
                for result in getData:
                    if result['status']: 
                        mainstatus = "Yes" 
                    else:
                        mainstatus = "No"
                        
                    data['Url'] = result['url']
                    data['ProProcessedcess'] = mainstatus
                    xls = xls.append(data, ignore_index=True)
                    xls.index += 1
                #now save the files
                #save as excel
                try:
                    filesaveName = self.internal.upper() + "_Categories.xlsx"
                    xls.to_excel(filesaveName)
                    webbrowser.open(getcwd())
                    savepath  = path.join(getcwd(), filesaveName)
                    print("Saved successfully to ", savepath)
                except Exception as e:
                    print("Error can not save ", e)
            else:
                print("No Extracted Categories data to save")
            
            self.saveData()
            
        elif step ==3:
            xls = pd.DataFrame(columns=['Brandname', 'Main Category', 'Sub Categories', 'Title', 'Images', 'Price', 'Selling Price', 'Discount', 'Description', 'Product Code', 'Review', 'Link'])
            
            getData = self.db.fetch(f"SELECT * FROM ddata ORDER BY brandname ASC ")
            if len(getData):
        
                print("Saving Datas to exceel sheet")
                for result in getData:
                    des = result['description'].decode()
                    data['Brandname'] = result['brandname']
                    data['Main Category'] = result['main_category']
                    data['Sub Categories'] = result['sub_categories']
                    data['Title'] = result['title']
                    data['Images'] = result['images']
                    data['Price'] = result['price']
                    data['Selling Price'] = result['selling_price']
                    data['Discount'] = result['discount']
                    data['Description'] = des
                    data['Product Code'] = result['product_code']
                    data['Review'] = result['review']
                    data['Link'] = result['link']
                    xls = xls.append(data, ignore_index=True)
                    xls.index += 1
                #now save the files
                #save as excel
                try:
                    filesaveName =  self.internal.upper() + "_Details.xlsx"
                    xls.to_excel(filesaveName)
                    webbrowser.open(getcwd())
                    savepath  = path.join(getcwd(), filesaveName)
                    print("Saved successfully to ", savepath)
                except Exception as e:
                    print("Error can not save ", e)
            else:
                print("No Extracted Detail data to save")
            
            self.saveData()
            
        else:
            sys.exit()
            
if __name__ == '__main__':
    stp = int(input("Choose site you want to start scrapping\n\n1. Konga.com\n2. Jumia.com\n3. Jiji.com\n\nSelect option now:  "))
    if stp ==1:
        Scrapp("konga","https://konga.com", "mainContent","","_06822_e7mpG").run()
        
    elif stp ==2:
        Scrapp("jumia","https://www.jumia.com.ng", "","has-b2top","-pvs").run()
        
    elif stp ==3:
        print("Sorry features not available")
    else:
        print("Oop nothing was selected")
    
 
 
