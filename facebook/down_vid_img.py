from facebook_scraper import _scraper, get_posts
import pandas as pd
import urllib.request, pandas as uuid
import os
import cv2
import datetime

driver = None
limit = datetime.timedelta(seconds=600)

if __name__ == '__main__':

    ids = ["https://facebook.com/" + line.split("/")[-1] for line in open("input.txt", newline='\n')]

    email = "" 
    password = ""

    input_lines = []

    with open('credentials.txt', 'r') as file:
        input_lines = [line.strip() for line in file]
        
    email = input_lines[0] 
    password = input_lines[1] 

    _scraper.login(email,password)
    ori_direc = os.getcwd()

    for id in ids:

        id = id.strip()
        os.chdir(ori_direc)
        folder = os.path.join(os.getcwd(), "Data")
        foldername = id.split('/')[-1].replace("?","_").replace("=","_").replace(".","_")
        folder = os.path.join(folder, foldername)
        df = pd.read_csv("Data/"+foldername+"/posts_data.csv")
        df = df.fillna('')

        if not os.path.exists(os.path.join(folder, 'media')):
            os.mkdir(os.path.join(folder, 'media'))
        new_path = os.path.join(folder, 'media')
        os.chdir(os.path.join(folder, 'media'))

        i = 1
        for index, row in df.iterrows():
            try:
                if len(row['Video Link'])>0 : 

                    link = row['Video Link']

                    for post in get_posts(post_urls = [link]):

                        link = post['video']
                        data = cv2.VideoCapture(link)

                        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
                        fps = data.get(cv2.CAP_PROP_FPS)
                        seconds = round(frames / fps)
                        video_time = datetime.timedelta(seconds=seconds)
                        print(video_time,end='     ')

                        if limit > video_time: 
                            urllib.request.urlretrieve(link, row['Video'])
                            print('video of post '+str(i)+' downloaded')
                        else: print('video of post '+str(i)+' not downloaded as video length is greater than 10 mins')
    

                elif len(row['Images Links'])>0 :

                    links = row['Images Links'].split(',') 
                    names = row['Images'].split(',') 

                    for count, link in enumerate(links):
                        urllib.request.urlretrieve(link.strip(), names[count].strip())

                    print('images of post '+str(i)+' downloaded')

                else: continue

            except: pass
            i += 1