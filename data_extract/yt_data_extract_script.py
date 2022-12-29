from pytube import YouTube, extract
from pytube.cli import on_progress
from moviepy.editor import *
import os, uuid, cv2, pandas as pd
from itertools import islice
from youtube_comment_downloader import *

def fetch_comments(link):

    comments = []

    while True:

        try:
            downloader = YoutubeCommentDownloader()
            comments_list = []
            comments = downloader.get_comments_from_url(link, sort_by=SORT_BY_POPULAR)
            break
        
        except:
            continue

    for comment in islice(comments, 10):
        comments_list.append(comment['text'])
    
    return comments_list


def DownloadYoutube(link, id, new_df):

    name = ''

    try:
        youtubeObject = YouTube(link, on_progress_callback=on_progress)

        new_df[id]['title'] = youtubeObject.title
        new_df[id]['description'] = youtubeObject.description
        new_df[id]['comments'] = fetch_comments(link)
        new_df[id]['filenames'] = []

        youtubeObject = youtubeObject.streams.get_highest_resolution()

        name = str(uuid.uuid4()) + '.mp4'
        youtubeObject.download(output_path='videos',filename=name)
        print("Download is completed successfully")

    except:
        name = ''
        print("An error has occurred")

    return name, new_df

def convert_to_seconds(time):

    time_div = time.split(':')
    m_arr = [1,60,60*60]
    seconds = 0

    for count, time in enumerate(reversed(time_div)):
        seconds += int(time)*m_arr[count]    

    return seconds

def collect_images(path ,img_nos):

    cam = cv2.VideoCapture(path+".mp4")
    totframe = 0
  
    while(True):
      
        ret, frame = cam.read()
        if ret: totframe += 1
        else: break

    cam.release()
    cam = cv2.VideoCapture(path+".mp4")

    curr_frame = 0
    capt_inc = int(totframe/(img_nos+1))
    capt_pnt = int(totframe/(img_nos+1))
    orig_img_nos = img_nos

    if not os.path.exists(path):
        os.mkdir(path)

    while img_nos != 0:
      
        ret, frame = cam.read()
        if ret:

            if curr_frame == capt_pnt:
                
                name = path +'/frame'+ str(curr_frame) + '.jpg'
                cv2.imwrite(name, frame)
                capt_pnt += capt_inc
                img_nos -= 1
                
            curr_frame += 1

        else:
            break
    
    cam.release()
    cv2.destroyAllWindows()

    print('Collected '+str(orig_img_nos)+' images from video\n\n')


def crop_out_video(filename, timefetch, emotion, id, new_df):

    timelimits = timefetch.split('-')
    start_time = timelimits[0].strip()
    end_time = timelimits[1].strip()
            
    start_time = convert_to_seconds(start_time)
    end_time = convert_to_seconds(end_time)

    emotion = row['Emotion']
            
    video = VideoFileClip('videos/'+filename).subclip(start_time, end_time)

    if not os.path.exists('cropped_videos/'+emotion):
        os.mkdir('cropped_videos/'+emotion)
            
    new_filename = str(uuid.uuid4())
    new_df[id]['filenames'].append(new_filename+ '.mp4')
    video.write_videofile('cropped_videos/'+emotion+'/'+new_filename+ '.mp4') 
    video.close()
    print('\nVideo '+str(index)+' downloaded')

    collect_images('cropped_videos/'+emotion+'/'+new_filename, 6)

    return new_df


if __name__ == '__main__':

    df = pd.read_csv('video_data_url.csv')

    new_df = {}

    link_y_map = {}

    if not os.path.exists('videos'):
        os.mkdir('videos')

    if not os.path.exists('cropped_videos'):
        os.mkdir('cropped_videos')
    
    for index, row in df.iterrows():
        
        link = row['Url']

        id = extract.video_id(link)

        if id in link_y_map:
            filename = link_y_map[id]
        else:
            new_df[id] = {}
            new_df[id]['emotion'] = row['Emotion']
            filename, new_df = DownloadYoutube(link, id, new_df)
            link_y_map[id] = filename
    
        if len(filename)>0:

            new_df = crop_out_video(filename, row['Timestamp'], row['Emotion'], id, new_df)

    post_df = pd.DataFrame.from_dict(new_df)
    post_df = post_df.transpose()
    post_df.to_csv('cropped_videos/posts_data.csv', encoding='utf-8-sig')

