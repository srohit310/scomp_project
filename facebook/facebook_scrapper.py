from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from dateutil.relativedelta import relativedelta

import platform, time, sys, os, shutil, urllib.request, pandas as pd, re, uuid

import json

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        'Accept-Language': 'en-US,en;q=0.5'}
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 
          'June': 6, 'July': 7, 'August': 8, 'September': 9, 
          'October': 10, 'November': 11, 'December': 12}

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

driver = None
f = open('out.txt', 'w', encoding="utf-8")

def add_to_link(id, addon):

    if '?' in id:
        driver.get(id + "&sk="+addon)
    else: driver.get(id + '/'+addon)


def get_posts():

    currentTimeDate = datetime.now() - relativedelta(years=10)
    currentTime = currentTimeDate
    
    df = {'Posted By': [], 'Post': [], 'Date': [], 'No. Likes': [], 'No. Comments': [], 'No. Shares': [], 'Images': [], 'Images Links': [], 'Video': [], 'Video Link': [], 'Comments':[]}

    n_posts_saved = 0
    date_passed_bool = 0
    
    run_bool = True

    keywords = [[['a','x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm','0'],
                 ['span','x4k7w5x x1h91t0o x1h9r5lt xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j x1jfb8zj','0']],
                [['h2'],
                 ['h3']],
                [['div'],
                 ['span']],
                [['x16hj40l','-1'],
                 ['x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1nxh6w3 x1sibtaa x1s688f x17z8epw','0']],
                [['x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xi81zsa'],
                 ['x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1nxh6w3 x1sibtaa x1s688f x17z8epw']]]

    posts = []
    posts_id_set = {'a'}
    
    while run_bool:

        new_posts = driver.find_elements(By.XPATH, "//div[contains(@class,'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')]")

        i = 0
        for new_item in reversed(new_posts):
            if new_item._id not in posts_id_set:
                i+=1
                posts_id_set.add(new_item._id)
            else: break

        for j in range(len(new_posts)-i,len(new_posts)):
            posts.append(new_posts[j])

        n_posts = len(posts)

        if (n_posts == n_posts_saved) or (n_posts_saved > 150) or date_passed_bool:
            post_df = new = pd.DataFrame.from_dict(df)
            post_df.to_csv('posts_data.csv', encoding='utf-8-sig')
            break
        
        driver.execute_script("arguments[0].scrollIntoView(true);", posts[n_posts_saved])
        driver.execute_script("this.scrollBy(0, -100)")
        time.sleep(1.0)
        
        temp = n_posts_saved

        for j in range(temp, temp+1):
            
            try:

                posts = driver.find_elements(By.XPATH, "//div[contains(@class,'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')]")
                is_reel = 0

                try:
                    posts[j].find_element(By.XPATH, ".//div[contains(@class, 'x78zum5 x5yr21d xl56j7k x1n2onr6 xh8yej3')]")
                    is_reel = 1

                except: pass
                
                post_id = posts[j].find_elements(By.XPATH, ".//"+keywords[0][is_reel][0]+"[contains(@class, '"+keywords[0][is_reel][1]+"')]")[int(keywords[0][is_reel][2])]

                hover = ActionChains(driver)

                date_posted = ''
                
                for i in range(1,10):
                    hover.move_to_element(post_id).perform()
                    try:
                        date_container = driver.find_element(By.XPATH, "//span[contains(@class, 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1nxh6w3 x1sibtaa xo1l8bm xzsf02u x1yc453h')]")
                        date_posted = date_container.get_attribute("innerText")

                    except: continue

                    date = date_posted[date_posted.find(',')+1:date_posted.find(' at')].strip().split(' ')

                    date[1] = str(months[date[1]])
                    date = "/".join(date[::-1])
                    datetime_object = datetime.strptime(date, "%Y/%m/%d")

                    if datetime_object<currentTime:
                        print('scrapped all posts posted within 1 year')
                        date_passed_bool = 1
                    break

                if date_passed_bool == 1:
                    break
                

                video_link = ""
                video_name = ""

                present = 1

                try:
                    posts[j].find_element(By.XPATH, ".//div[contains(@class, 'x1ey2m1c x9f619 xds687c x10l6tqk x17qophe x13vifvy x1ypdohk')]")
                    present = 1

                except: 

                    if not is_reel: 
                        present = 0
                
                if present == 1:

                    video_name = str(uuid.uuid4()) + '.mp4'
                    if is_reel:
                        link_container = posts[j].find_element(By.XPATH, ".//a[contains(@class, 'x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1rg5ohu x1a2a7pz x1n2onr6 xh8yej3')]")
                        video_link = link_container.get_attribute("href")
                    else: video_link = post_id.get_attribute("href")

                posted_by = driver.execute_script("return arguments[0].querySelector('"+keywords[1][is_reel][0]+"').getElementsByClassName('xt0psk2')[0].innerText", posts[j])

                text = ""
                try:
                    try:
                        elements = posts[j].find_elements(By.XPATH, ".//div[contains(@class, 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f')]")
                        for e in elements:
                            if e.text == 'See more':
                                e.click()
                                time.sleep(0.5)
                            else:
                                pass
                    except:
                        pass

                    texts = posts[j].find_elements(By.XPATH, ".//"+keywords[2][is_reel][0]+"[contains(@dir, 'auto')]")

                    for text_unit in texts:
                        try:
                            text += text_unit.text
                        except: pass

                except:
                    text = ""


                img_links = []
                img_names = []

                imgs = []
                try:
                    fetch_images = posts[j].find_elements(By.XPATH, ".//div[contains(@class, 'x10l6tqk x13vifvy')]/img")
                    imgs.extend(fetch_images)
                except: pass

                try:
                    fetch_images = posts[j].find_elements(By.XPATH, ".//img[contains(@class, 'x1rg5ohu x5yr21d xl1xv1r xh8yej3')]")
                    imgs.extend(fetch_images)
                except: pass

                for img in imgs:
                    try:
                        img_url = img.get_attribute('src')
                        img_name = str(uuid.uuid4()) + '.jpg'
                        img_names.append(img_name)
                        img_links.append(img_url)
                    except: pass


                try:
                    likes = posts[j].find_elements(By.XPATH, ".//span[contains(@class, '"+keywords[3][is_reel][0]+"')]")[int(keywords[3][is_reel][1])].get_attribute('innerText')
                except:
                    likes = '0'

                n_comments = ''
                n_shares = ''

                try:
                    comments_shares = posts[j].find_elements(By.XPATH, ".//span[contains(@class, '"+keywords[4][is_reel][0]+"')]")

                    if is_reel:
                        n_comments, n_shares = comments_shares[1].get_attribute("innerText"), comments_shares[2].get_attribute("innerText")
                    elif len(comments_shares) == 3:
                        n_text = comments_shares[2].text
                        if "comment" in n_text:
                            n_comments, n_shares = n_text, '0 '
                        else:
                            n_comments, n_shares = '0 ', n_text
                    else:
                        n_comments, n_shares = comments_shares[2].text, comments_shares[3].text
                except:
                    n_comments, n_shares = '0 ', '0 '


                try:
                    comments_list = []
                    comments = posts[j].find_elements(By.XPATH, ".//div[contains(@class,'x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi')]")

                    for comment in comments:
                        comment_text = comment.find_element(By.XPATH, ".//div[contains(@class,'x1lliihq xjkvuk6 x1iorvi4')]")
                        comment_text = comment_text.get_attribute('innerText')
                        comments_list.append(comment_text)

                except: pass

                n_posts_saved += 1

                df["Posted By"].append(posted_by)
                df['Post'].append(text)
                df['Date'].append(date_posted)
                df['Images'].append(", ".join(img_names))
                df['Images Links'].append(", ".join(img_links))
                df['Video'].append(video_name)
                df['Video Link'].append(video_link)
                df['No. Likes'].append(likes)
                df["No. Comments"].append(n_comments)
                df["No. Shares"].append(n_shares)
                df["Comments"].append(comments_list)

                print('post '+str(n_posts_saved)+' fetched')

            except: 

                n_posts_saved += 1
                continue
            
            

    
def get_about(id):
    sub_urls = {
        "Work and Education": "about_work_and_education",
        "Places lived": "about_places",
        "Contact and basic info": "about_contact_and_basic_info",
        "Family and relationships": "about_family_and_relationships",
        "Details": "about_details",
    }
    
    df = {}

    for key, value in sub_urls.items():

        add_to_link(id, value)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "x1yztbdb")))
        items = driver.find_elements(By.XPATH, "//div[contains(@class,'xyamay9 xqmdsaz x1gan7if x1swvt13')]/div")

        for count, item in enumerate(items):
            title_container = item.find_element(By.XPATH, ".//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u') and contains(@dir,'auto')]")
            title = title_container.get_attribute("innerText")
            values_list = item.find_elements(By.XPATH, ".//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u') and contains(@dir,'auto')]")
            list_of_items = {}
            for x in values_list:
                try:
                    link = x.find_element(By.XPATH, ".//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f')]")
                    list_of_items[x.get_attribute("innerText")] = link.get_attribute("href")
                except:
                    list_of_items[x.get_attribute("innerText")] = "not available"

            df[title] = [list_of_items]
    
    post_df = pd.DataFrame.from_dict(df)
    post_df.to_csv('about_data.csv', encoding='utf-8-sig')



def more_data(id):

    categories = ['sports','music','movies','tv','books','games']

    joiner = '/'
    if '?' in id: joiner = '&sk='
    df = {'sports':[],'music':[],'movies':[],'tv':[],'books':[],'games':[]}

    for category in categories:
        driver.get(id+joiner+category)
        category_list = []
        if category in ['sports','games']:
            elements = driver.find_elements(By.XPATH, "//div[contains(@class,'x78zum5 x1q0g3np x1a02dak')]/div[contains(@class,'x9f619 x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6')]")
            for element in elements:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    driver.execute_script("this.scrollBy(0, -100)")
                    time.sleep(0.05)
                    link = element.find_element(By.XPATH, ".//div/div/a")
                    category_list.append(link.get_attribute("href"))
                except:
                    break

        else:
            elements = driver.find_elements(By.XPATH, "//div[contains(@class,'x78zum5 x1q0g3np x1a02dak x1qughib')]/div")
           
            for element in elements:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    driver.execute_script("this.scrollBy(0, -100)")
                    time.sleep(0.05)
                    link = element.find_element(By.XPATH, ".//div/a")
                    category_list.append(link.get_attribute("href"))
                except:
                    break

        df[category].append(category_list)
    
    post_df = pd.DataFrame.from_dict(df)
    post_df.to_csv('more_data.csv', encoding='utf-8-sig')
    
    
def get_friends(id):
    
    n_friends_saved = 0
    run_bool = True

    add_to_link(id, 'friends_all')
    time.sleep(1.0)

    item_no = 0

    try:
        driver.find_element(By.XPATH, "//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xtoi2st x3x7a5m x1603h9y x1u7k74 x1xlr1w8 x12scifz x2b8uid')]")
        print('\nThe user has too many followers as a result the list is not generated')
        
        add_to_link(id, 'following')
        time.sleep(1.0)
        
        item_no = 1

        driver.find_element(By.XPATH, "//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xtoi2st x3x7a5m x1603h9y x1u7k74 x1xlr1w8 x12scifz x2b8uid')]")
        print('\nThe user has too many followings as a result the list is not generated')

        return

    except: pass

    friends_no_cont = driver.find_elements(By.XPATH, "//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f')]")

    friends_no = friends_no_cont[item_no].get_attribute("innerText")
    friends_no = int(friends_no.split(' ')[0])

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    df = {'friends':[]}

    while run_bool:
        
        friends = driver.find_elements(By.XPATH, "//div[contains(@class,'x78zum5 x1q0g3np x1a02dak x1qughib')]/div")
      
        n_friends = len(friends)-1
    
        if (n_friends_saved > 50):
                break
        
        if (n_friends == n_friends_saved) and (n_friends < friends_no):
                
            while n_friends == n_friends_saved:
                friends = driver.find_elements(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p  _ab9- _aba8 _abcm')]")
                n_friends = len(friends)
        
        if (n_friends == n_friends_saved) or (n_friends_saved > 50):
            break
        
        # scroll to next
        driver.execute_script("arguments[0].scrollIntoView(true);", friends[n_friends_saved])
        driver.execute_script("this.scrollBy(0, -100)")
        time.sleep(0.05)

        temp = n_friends_saved

        for j in range(temp, temp+1):
            
            friend = friends[j].find_element(By.XPATH, ".//div[2]/div[1]/a")
            df['friends'].append(friend.get_attribute("href"))
            n_friends_saved += 1
    
    post_df = pd.DataFrame.from_dict(df)
    post_df.to_csv('friends_data.csv', encoding='utf-8-sig')


def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "Data")

    if not os.path.exists(folder):
        os.mkdir(folder)

    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for id in ids:
        id = id.strip()
        foldername = id.split('/')[-1].replace("?","_").replace("=","_").replace(".","_")
        if os.path.exists(os.path.join(folder, foldername)):
            shutil.rmtree(os.path.join(folder, foldername))

        driver.get(id)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "x7wzq59")))

        print("\nScraping: "+ id+"\n\n")

        try:
            if not os.path.exists(os.path.join(folder, foldername)):
                os.mkdir(os.path.join(folder, foldername))
            else:
                f.write("A folder with the same profile name already exists."
                      " Kindly remove that folder first and then run this code.")
                continue
            os.chdir(os.path.join(folder, foldername))
        except:
            f.write("Some error occurred in creating the profile directory.")
            continue
    
        get_posts()
        
        # try:
        #     get_friends(id)
        # except: pass

        # try:
        #     more_data(id)
        # except: pass
        
        # try:
        #     get_about(id)
        # except: pass



def login(email, password):
    """ Logging into our own profile """

    try:
        global driver

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("headless")

        try:
            platform_ = platform.system().lower()
            if platform_ in ['linux', 'darwin']:
                service = Service('./chromedriver')
            else:
                service = Service('./chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capabilities)
        except:
            f.write("Kindly replace the Chrome Web Driver with the latest one from"
                  "http://chromedriver.chromium.org/downloads"
                  "\nYour OS: {}".format(platform_)
                 )
            exit()
        driver.get("https://facebook.com")
        driver.maximize_window()

        # filling the form
        #driver.find_element_by_name('email').send_keys(email)
        driver.find_element(By.NAME, 'email').send_keys(email)
        #driver.find_element_by_name('pass').send_keys(password)
        driver.find_element(By.NAME, 'pass').send_keys(password)

        # clicking on login button
        #driver.find_element_by_name("login").click()
        driver.find_element(By.NAME, "login").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "x1iyjqo2")))
        
        return driver

    except Exception as e:
        f.write("There's some error in log in.")
        f.write(str(sys.exc_info()[0]))
        exit()

def main():
    ids = ["https://facebook.com/" + line.split("/")[-1] for line in open("input.txt", newline='\n')]
    if len(ids) > 0:

        email = "" 
        password = ""

        input_lines = []

        with open('credentials.txt', 'r') as file:
            input_lines = [line.strip() for line in file]
        
        email = input_lines[0] 
        password = input_lines[1] 

        f.write("\nStarting Scraping...")

        login(email, password)
        scrap_profile(ids)
        driver.close()

    else:

        f.write("Input file is empty..")


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

if __name__ == '__main__':
    # get things rolling
    main()