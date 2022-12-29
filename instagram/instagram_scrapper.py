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
import json

import platform, time, sys, os, shutil, urllib.request, pandas as pd, re, uuid

import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        'Accept-Language': 'en-US,en;q=0.5'}

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
driver = None
f = open('out.txt', 'w', encoding="utf-8")


def get_posts():

    currentTimeDate = datetime.now() - relativedelta(years=10)
    currentTime = currentTimeDate
    
    df = {'Posted By': [], 'Post': [], 'Date': [], 'No. Likes': [], 'Images': [], 'Images Links': [], 'Video': [], 'Video Link': [], 'Comments':[], 'Tags':[]}

    n_posts_saved = 0
    date_passed_bool = 0
    
    run_bool = True
    posts = []
    posts_id_set = {'a'}

    while run_bool:

        new_posts = driver.find_elements(By.XPATH, "//div[contains(@class,'_aabd _aa8k _aanf')]")
        
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
            post_df = pd.DataFrame.from_dict(df)
            post_df.to_csv('posts_data.csv', encoding='utf-8-sig')
            break
        
        driver.execute_script("arguments[0].scrollIntoView(true);", posts[n_posts_saved])
        driver.execute_script("this.scrollBy(0, -100)")
        
        time.sleep(0.5)
        temp = n_posts_saved

        for j in range(temp, temp+1):
            
            posts[j].click()
            
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ".//ul[contains(@class,'_a9ym')]")))
            except: pass
                        
            date_container = driver.find_element(By.XPATH, "//div[contains(@class, '_aacl _aacm _aacu _aacy _aad6')]/time")
            date_posted = date_container.get_attribute("datetime")

            date = date_posted[:date_posted.find('T')]
            datetime_object = datetime.strptime(date, "%Y-%m-%d")
            
            if datetime_object<currentTime:
                print('scrapped all posts posted within 1 year')
                date_passed_bool = 1
            
            if date_passed_bool == 1:
                break

            video_link = ""
            video_name = ""
            
            present = 0

            try:
                driver.find_element(By.XPATH, "//video[contains(@class, '_ab1d')]")
                present = 1
            except: present = 0

            if present == 1:
                
                post_id_cont = driver.find_element(By.XPATH, "//div[contains(@class,'_aacl _aaco _aacu _aacx _aad6 _aade _aaqb')]/a")
                video_link = post_id_cont.get_attribute('href')
                video_name = str(uuid.uuid4()) + '.mp4'

            posted_by_element = driver.find_element(By.XPATH, "//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _acan _aiit _acao _aija _acat _acaw _aj1- _a6hd')]")
            posted_by = posted_by_element.get_attribute("innerText")


            text = ""
            try:
                text_container = driver.find_element(By.XPATH, "//div[contains(@role, 'button') and contains(@class,'_aa06') and contains(@tabindex,'0')]/li/div")
                text_element = text_container.find_element(By.XPATH, "//span[contains(@class,'_aacl _aaco _aacu _aacx _aad7 _aade')]")
                text = text_element.get_attribute("innerText")

            except:
                text = ""

            tags = []
            try:
                tags_container = driver.find_elements(By.XPATH, "//a[contains(@class, 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _aa1q _a6hd')]")
                for tag in tags_container:
                    tag_tuple = (tag.get_attribute('href'),tag.get_attribute('innerText'))
                    tags.append(tag_tuple)
            except: pass

            img_links = ""
            img_names = ""
            
            try:
                post_container = driver.find_element(By.XPATH, "//div[contains(@class, '_aatk _aatl')]")

                img = post_container.find_element(By.XPATH, ".//img[contains(@class, 'x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3')]")
                img_url = img.get_attribute('src')
                img_name = str(uuid.uuid4()) + '.jpg'
                img_names = img_name
                img_links = img_url
            except:
                pass

            likes = ""

            try:
                text2 = driver.find_element(By.XPATH, "//div[contains(@class, '_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9o _ab9r  _aba- _abbg _abby _abce _abcm')]")
                likes = text2.get_attribute('innerText')
            except:
                likes = '0'

            
        try:
            comments_list = []
            comments = driver.find_elements(By.XPATH, ".//ul[contains(@class,'_a9ym')]")
            for comment in comments:
                comment_text = comment.find_element(By.XPATH, ".//span[contains(@class,'_aacl _aaco _aacu _aacx _aad7 _aade')]")
                comment_text = comment_text.get_attribute('innerText')
                comments_list.append(comment_text)

        except: pass

        close_element = driver.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl x6umtig x1b1mbwd xaqea5y xav7gou x9f619 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x6s0dn4 x78zum5 xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x1ypdohk xl56j7k x1y1aw1k x1sxyh0 xwib8y2 xurb0ha')]")
        close_element.click()
            
        n_posts_saved += 1

        df["Posted By"].append(posted_by)
        df['Post'].append(text)
        df['Date'].append(date_posted)
        df['Images'].append(img_names)
        df['Images Links'].append(img_links)
        df['Video'].append(video_name)
        df['Video Link'].append(video_link)
        df['No. Likes'].append(likes)
        df["Comments"].append(comments_list)
        df['Tags'].append(tags)

        print('post '+str(n_posts_saved)+' fetched')
        

    
def get_about():
    
    df = {}

    user_id_container = driver.find_element(By.XPATH, "//h2[contains(@class,'_aacl _aacs _aact _aacx _aada')]")
    user_id = user_id_container.get_attribute("innerText")

    numeric_info = driver.find_elements(By.XPATH, "//li[contains(@class,' xl565be    x2pgyrj  x1m39q7l x1uw6ca5')]")
    
    posts = numeric_info[0].get_attribute("innerText")
    followers = numeric_info[1].get_attribute("innerText")
    following = numeric_info[2].get_attribute("innerText")

    bio_info = driver.find_element(By.XPATH, "//div[contains(@class,'_aa_c')]")
    bio = bio_info.get_attribute("innerText")
    if "Followed by" in bio:
        bio = bio[:bio.find("Followed by")]

    df["User_ID"] = user_id
    df["no_posts"] = posts
    df["no_followers"] = followers
    df["no_following"] = following
    df["bio"] = bio
    
    post_df = pd.DataFrame(df, index=[0])
    post_df.to_csv('about_data.csv', encoding='utf-8-sig')
    
    
def get_following():
    
    following_container = driver.find_elements(By.XPATH, "//li[contains(@class,' xl565be    x2pgyrj  x1m39q7l x1uw6ca5')]")[2]
    following_no = int(''.join(list(filter(str.isdigit, following_container.get_attribute("innerText")))))
    following_container.click()

    time.sleep(2.0)

    for i in range(0,2):

        n_elements_saved = 0
        run_bool = True
        df = {}
        elements_no = 0
        if i == 0:
            df = {'following_name':[], 'following_id':[]}
            elements_no = following_no
        if i == 1:
            driver.find_elements(By.XPATH, "//div[contains(@class,'_acbs')]/div")[1].click()
            time.sleep(2.0)
            df = {'hashtag_name':[], 'hashtag_link':[]}

        while run_bool:

            elements = driver.find_elements(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p  _ab9- _aba8 _abcm')]")
            
            n_elements = len(elements)
            if i == 1: elements_no = n_elements

            if (n_elements_saved > 50):
                break

            if (n_elements == n_elements_saved) and (n_elements < elements_no):
                time.sleep(2.0)
                
                while n_elements == n_elements_saved:
                    elements = driver.find_elements(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p  _ab9- _aba8 _abcm')]")
                    n_elements = len(elements)

            elif (n_elements == n_elements_saved):
                break 
            
            # scroll to next
            class_name = ""
            if i == 0:
                class_name = '_aano'
            else: class_name = '_aabq'
            scr1 = driver.find_element(By.XPATH, "//div[contains(@class,'"+class_name+"')]")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scr1)
            driver.execute_script("arguments[0].scrollIntoView(true);", elements[n_elements_saved])
            driver.execute_script("this.scrollBy(0, -100)")

            temp = n_elements_saved

            for j in range(temp, temp+1):
                
                if i == 0:
                    following_name = "not avalailable"
                    following_link = ""
                    friend_link_container = elements[j].find_element(By.XPATH, ".//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz notranslate _a6hd')]")
                    following_link = friend_link_container.get_attribute("href")
                    try:
                        friend_name_container = elements[j].find_element(By.XPATH, ".//div[contains(@class,'_aacl _aaco _aacu _aacy _aada')]")
                        following_name = friend_name_container.get_attribute("innerText")
                    except: pass
                    df['following_name'].append(following_name)
                    df['following_id'].append(following_link)
                else:
                    hashtag_container = elements[j].find_element(By.XPATH, ".//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _aabs  _aa9_ _a6hd')]")
                    hashtag_link = hashtag_container.get_attribute("href")
                    hashtag_name = hashtag_container.get_attribute("innerText")
                    df['hashtag_name'].append(hashtag_name)
                    df['hashtag_link'].append(hashtag_link)
                
                n_elements_saved += 1
    
            post_df = pd.DataFrame.from_dict(df)
            if i == 1: filename = 'hashtag_data.csv'
            else: filename = 'friends_data.csv'
            post_df.to_csv(filename, encoding='utf-8-sig')




def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "instagram_data")

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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'_aa_y _aa_z _aa_-')]")))


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
        
        get_about()
        get_posts()
        # get_following()


def login(username, password):
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
        driver.get("https://www.instagram.com")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))

        driver.maximize_window()
        # filling the form
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        # clicking on login button
        driver.find_element(By.XPATH, "//button[contains(@class,'_acan _acap _acas')]").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//main[contains(@class,'x78zum5 xdt5ytf x1iyjqo2 x182iqb8 xnz67gz')]")))
        return driver

    except Exception as e:
        exit()
        

def main():
    ids = ["https://www.instagram.com/" + line.split("/")[-1] for line in open("input.txt", newline='\n')]
    if len(ids) > 0:
        # Getting email and password from user to login into his/her profile
        username = ""
        password = ""
        input_lines = []

        with open('credentials.txt', 'r') as file:
            input_lines = [line.strip() for line in file]
        
        username = input_lines[0] 
        password = input_lines[1] 
        
        login(username, password)
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