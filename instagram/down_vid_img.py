from instaloader import *
import pandas as pd
import urllib.request
import os

L = instaloader.Instaloader()

driver = None

if __name__ == '__main__':

    ids = ["https://www.instagram.com/" + line.split("/")[-1] for line in open("input.txt", newline='\n')]

    email = "" 
    password = ""

    input_lines = []

    with open('credentials.txt', 'r') as file:
        input_lines = [line.strip() for line in file]
        
    email = input_lines[0] 
    password = input_lines[1] 

    L.login(email, password)
    
    ori_direc = os.getcwd()

    for id in ids:

        id = id.strip()
        os.chdir(ori_direc)
        folder = os.path.join(os.getcwd(), "instagram_data")
        foldername = id.split('/')[-1].replace("?","_").replace("=","_").replace(".","_")
        folder = os.path.join(folder, foldername)
        df = pd.read_csv("instagram_data/"+foldername+"/posts_data.csv")
        df = df.fillna('')

        if not os.path.exists(os.path.join(folder, 'media')):
            os.mkdir(os.path.join(folder, 'media'))
        new_path = os.path.join(folder, 'media')
        os.chdir(os.path.join(folder, 'media'))

        i = 1

        for index, row in df.iterrows():
        
            if len(row['Video Link'])>0 : 

                link = row['Video Link']
                name = row['Video']
                SHORTCODE = link.split('/')[-2]
                
                post = Post.from_shortcode(L.context, SHORTCODE)
                link = post.video_url

                urllib.request.urlretrieve(link, name)
                
                print('video of post '+str(i)+' downloaded')
                
            elif len(row['Images Links'])>0 :
                
                link = row['Images Links']
                name = row['Images']

                urllib.request.urlretrieve(link, name)

                print('images of post '+str(i)+' downloaded')
                
            else: pass

            i+=1