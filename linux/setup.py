from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import threading
from os import path
from os import getcwd
import pandas as pd
from dclass import respath, remoteread_file, pprint, Db
from time import sleep
import webbrowser


savefilename = 'Konga' #name of excel/html sheet you want to save with with no extension
savepath_to = path.join(getcwd(), savefilename)

class Konga:
    
    def __init__(self):
        self.limit = 0
        self.url = 'https://konga.com'
        self.saveoutput = self.url.replace('https://', '').replace('.', '-') + '.xlsx'
        self.browserdriver = respath('driver/chromedriver.exe')
        self.category = []
        self.pages = []
        self.extractingdetails = 0
        self.dbname = 'kdb.db'
        self.db = Db(respath(self.dbname))
        self.createDB()

    def createDB(self):
           
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
            
    
    def dosubProcess(self):
        checkdb2 = self.db.check('id', 'dcategory', f"id!='0' ")
        if checkdb2:
            step = int(input("You have some unfinished processing. Select options to continue\n\n1. Continue Extract pages and Extract Details\n2. Export saved Details only\n3. Export saved Details and continue extracting\n4. Start new session : "))
            if step ==1:
                self.extractPages()
            elif step ==2:
                self.saveData()
            elif step ==3:
                self.extractPages()
                self.saveData()
            elif step ==4:
                self.db.check(f"DELETE FROM dcategory")
                self.db.check(f"DELETE FROM dpages")
                self.db.check(f"DELETE FROM ddata")
                self.dosubProcess()
            else:
                print("Sorry no option was select try again")
                self.dosubProcess()
        else:
            try:
                options = Options()
                options.add_argument('--ignore-certificate-errors')
                options.add_argument("--test-type")
                options.add_argument("--headless")
                browser = webdriver.Chrome(self.browserdriver, options=options)
                #try parsing with selenium
                browser.get(self.url)
                #wait for the browser page to load
                waitToLoad = WebDriverWait(browser, 5)
                #wait until the target class is loaded and found
                waitToLoad.until(EC.presence_of_element_located((By.ID, 'mainContent')))
                #if successfully loaded store it to pagecontents variable
                allcategories_link = browser.find_element_by_id("mainContent")
                dcontent = allcategories_link.get_attribute("outerHTML")
                print("Connecting to "+ str(savefilename))
            except:
                #try process with get
                dcontent = remoteread_file(self.url)
            finally:
                browser.quit()
            
            try:
                content = bs(dcontent, 'html.parser')
                
                for totalfound_href in content.find_all('a'):
                    foundurl = totalfound_href["href"]
                    
                    if "category" in foundurl:
                        if not foundurl.startswith('http') or not foundurl.startswith('https'):
                            foundurl = self.url+'/'+ foundurl.lstrip('/')
                        
                        checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                        if checkdb is None:
                            print("Category saved ", foundurl)
                            self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                            
                print("Categories saved successfully")
                
            except Exception as e:
                print('sub category error: '+ str(e))
        
            self.extractPages()
    
    def extractPages(self):
        print("Extracting pages... Please wait...")
        t2 =  threading.Thread(name='extracting details', target=self.extractDetails)
        if not t2.isAlive() or not t2.is_alive():
            if not self.extractingdetails:
                t2.start()
           
        while True:
            checkdb = self.db.check('id', 'dcategory', f"status='0' ")
            if checkdb is None:
                print("All Pages saved Successfully")
                break
                        
            getPages = self.db.fetch(f"SELECT * FROM dcategory WHERE status='0' ORDER BY id DESC ")
            if len(getPages):
                page = ''
                for pag in getPages:
                    page = pag['url']
                    try:
                        print("Processing page", page)
                        options = Options()
                        options.add_argument('--ignore-certificate-errors')
                        options.add_argument("--test-type")
                        options.add_argument("--headless")
                        browser = webdriver.Chrome(self.browserdriver, options=options)
                        #try parsing with selenium
                        browser.get(page)
                        #wait for the browser page to load
                        waitToLoad = WebDriverWait(browser, 5)
                        #wait until the target class is loaded and found
                        waitToLoad.until(EC.presence_of_element_located((By.ID, 'mainContent')))
                        #if successfully loaded store it to pagecontents variable
                        allcategories_link = browser.find_element_by_class_name('_06822_e7mpG')
                        dcontent = allcategories_link.get_attribute("outerHTML")
                    except:
                        #try process with get
                        dcontent = remoteread_file(page)
                    finally:
                        browser.quit()
                    
                    try:
                        content = bs(dcontent, 'html.parser')
                        
                        for totalfound_href in content.find_all('a'):
                            foundurl = totalfound_href["href"]
                            if not foundurl.startswith('http') or not foundurl.startswith('https'):
                                foundurl = self.url+'/'+ foundurl.lstrip('/')
                                
                            if "category" in foundurl:                               
                                checkdb = self.db.check('id', 'dcategory', f"url='{foundurl}' ")
                                if checkdb is None:
                                    print("Category saved ", foundurl)
                                    self.db.insert('dcategory', 'url, status', f"'{foundurl}', '0' ")
                            else:
                                checkdb = self.db.check('id', 'dpages', f"url='{foundurl}' ")
                                if checkdb is None:
                                    print("Page saved ", foundurl)
                                    self.db.insert('dpages', 'url, status', f"'{foundurl}', '0' ")
                                
                    except Exception as e:
                        print('pages or category error: '+ str(e))
                        
                    self.db.others(f"UPDATE dcategory SET status=1 WHERE id='{pag['id']}'")
                    sleep(2)
    
    def extractDetails(self):
        countfound = 0
        while True:
            self.extractingdetails = 1
            sleep(5)
            checkdb = self.db.check('id', 'dpages', f"status='0' ")
            if checkdb is None:
                print("All Datas saved Successfully")
                self.extractingdetails = 0
                break
            
            if self.limit:
                if self.limit >= countfound:
                    self.extractingdetails = 0
                    break
    
            getPage = self.db.fetch(f"SELECT * FROM dpages WHERE status='0' ORDER BY id ASC ")
            if len(getPage):
                print("Extracting Details from pages")
                page = ''
                for pag in getPage:
                    page = pag['url']
                    countfound +=1
                    if self.limit:
                        if self.limit >= countfound:
                            self.extractingdetails = 0
                            break
                    
                    try:
                        print("Extraction begins on page", page)
                        opts = Options()
                        opts.add_argument('--ignore-certificate-errors')
                        opts.add_argument("--test-type")
                        opts.add_argument("--headless")
                        browser = webdriver.Chrome(self.browserdriver, options=opts)
                        #try parsing with selenium
                        browser.get(page)
                        #wait for the browser page to load
                        waitToLoad = WebDriverWait(browser, 5)
                        #wait until the target class is loaded and found
                        waitToLoad.until(EC.presence_of_element_located((By.ID, 'mainContent')))
                        #if successfully loaded store it to pagecontents variable
                        allcategories_link = browser.find_element_by_id('mainContent')
                        dcontent = allcategories_link.get_attribute("outerHTML")
                        #with open("kongadetailpage2.htm", 'r') as rt:
                        #    dcontent = rt.read()
                        content = bs(dcontent, 'html.parser')
                        
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
                            #print("Description", resultDescription)
                            '''print("Main Category", resultMainsubcate)
                            print("Sub Categories", resultAllsubcate)
                            print("Images", str(resultImage))
                            print("Discount", resultPricesaved)
                            print("Selling Price", resultPricediscount)
                            print("Price", resultPrice)
                            print("Brandname", resultBrand)
                            print("Title", resultTitle)
                            print("Review", resultReview)
                            print("Product Code", resultProductCode)'''
                            checkdb = self.db.check('id', 'ddata', f"dpageid='{pag['id']}' ")
                            if checkdb is None:
                                print("Data saved ", resultTitle)
                                self.db.insert('ddata', 'dpageid,brandname,main_category, sub_categories,title,images,price,selling_price,discount,description,product_code,review, link', f"'{pag['id']}','{resultBrand}','{resultMainsubcate}','{resultAllsubcate}','{resultTitle}','{resultImage}','{resultPrice}','{resultPricediscount}','{resultPricesaved}','{resultDescription}','{resultProductCode}', '{resultReview}', '{page}' ")
                          
                        print("Finished extracting ", page)
                    
                    except Exception as e:
                        print('Error occurred '+ str(e))
                    finally:
                        browser.quit()
                        pass    
                    
                    self.db.others(f"UPDATE dpages SET status=1 WHERE id='{pag['id']}'" )
                                         
    def saveData(self):
        xls = pd.DataFrame(columns=['Brandname', 'Main Category', 'Sub Categories', 'Title', 'Images', 'Price', 'Selling Price', 'Discount', 'Description', 'Product Code', 'Review', 'Link'])
        data = {}
        
        getData = self.db.fetch(f"SELECT * FROM ddata ORDER BY brandname ASC ")
        if len(getData):
    
            print("Saving Datas to exceel sheet")
            for result in getData:
                data['Brandname'] = result['brandname']
                data['Main Category'] = result['main_category']
                data['Sub Categories'] = result['sub_categories']
                data['Title'] = result['title']
                data['Images'] = result['images']
                data['Price'] = result['price']
                data['Selling Price'] = result['selling_price']
                data['Discount'] = result['discount']
                data['Description'] = result['description']
                data['Product Code'] = result['product_code']
                data['Review'] = result['review']
                data['Link'] = result['link']
                xls = xls.append(data, ignore_index=True)
                xls.index += 1
            #now save the files
            #save as excel
            xls.to_excel(self.saveoutput)
            webbrowser.open(getcwd())
            print("All parsed and saved successfully")
        else:
            print("No data to save")
        
if __name__ == '__main__':
    Konga().dosubProcess()
    
 
 
