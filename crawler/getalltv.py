from bs4 import BeautifulSoup
import requests
import re
import pymongo
import os
from shutil import rmtree
from multiprocessing import Pool
import random
import json

proxy_list = [
    'http://218.202.111.10:80',
    'http://120.202.249.201:80',
    'http://58.49.164.222:8118',
    'http://120.202.249.202:8080',
    ]
proxy_ip = random.choice(proxy_list) # 随机获取代理ip
proxies = {'http': proxy_ip}


tv_cate={'war3':'魔兽争霸','overwatch':'守望先锋','sc2':'星际争霸','hots':'风暴英雄','how':'炉石传说'}

client = pymongo.MongoClient('localhost', 27017)
maintbl=client['maintbl']
livetbl=maintbl['livetbl']
livetbl.remove()


def init_crawl():

    path='D:/anyTv/version1.1/anytv/static/images/room_img/'
    if os.path.isdir(path):
        rmtree(path)
    os.mkdir(path)

def downloadpic(url,filename):
    r=requests.get(url,proxies=proxies)
    if r.status_code!=200:
        return
    room_img_path='D:/anyTv/version1.1/anytv/static/images/room_img/'
    target=room_img_path+filename
    with open(target,'wb') as fs:
        fs.write(r.content)



def get_douyu():
    url ='http://www.douyu.com/directory'
    wb_data = requests.get(url,proxies=proxies)
    if wb_data.status_code!=200:
        return
    soup=BeautifulSoup(wb_data.text,'lxml')

    douyu_channels=soup.select('li a.thumb')
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in douyu_channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append('http://www.douyu.com'+i.get('href'))
    return gamelist

def get_panda():
    url='http://www.panda.tv/cate'
    wb_data = requests.get(url)
    wb_data.encoding='utf-8'
    soup=BeautifulSoup(wb_data.text,'lxml')

    panda_channels=soup.select('li a.video-list-item-wrap')
    print(panda_channels)
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in panda_channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append('http://www.panda.tv'+i.get('href'))
    print(gamelist)

def get_zhanqi():
    wb_data = requests.get('http://www.zhanqi.tv/games')
    wb_data.encoding='utf-8'
    soup=BeautifulSoup(wb_data.text,'lxml')

    channels=soup.select('#game-list-panel li div a')
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append('http://www.zhanqi.tv'+i.get('href'))
    print(gamelist)

def get_huya():
    wb_data = requests.get('http://www.huya.com/g')
    soup=BeautifulSoup(wb_data.text,'lxml')

    channels=soup.select('a.pic.clickstat')
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append(i.get('href'))
    print(gamelist)



def get_douyu_all_info(game_channel):
    for page in range(1,10):
        url=game_channel+'?page={}&isAjax=1'.format(str(page))
        # print(page)
        wb_data=requests.get(url,proxies=proxies)
        soup=BeautifulSoup(wb_data.text,'lxml')
        # print(soup.prettify())
        roomlist=soup.findAll(attrs={'data-cid':True})
        for i in roomlist:
            room_obs=i.select("span.dy-num.fr")[0].text
            if '万' in room_obs:
                ob_num=int(float(room_obs.split('万')[0])*10000)
            else:
                ob_num=int(room_obs)
            if ob_num<=1:
                break

            room_no = i.select('a')[0].get('href')
            room_url='http://www.douyu.com'+room_no
            room_title=i.select('h3')[0].text
            room_owner=i.select("span.dy-name.ellipsis.fl")[0].text
            room_tag = i.select('span.tag.ellipsis')[0].text
            room_imgsrc = i.find('img',attrs={'data-original':True}).get('data-original')
            room_pic = '斗鱼'+room_no.strip('/')+'.jpg'
            # downloadpic(img,room_pic)
            room={
                'url':room_url,
                'data_from':'斗鱼',
                'title':room_title,
                'owner':room_owner,
                'tag':room_tag,
                'obs':room_obs,
                'ob_num':ob_num,
                'on_off':1,
                'room_pic':room_pic,
                'room_imgsrc':room_imgsrc
            }

            livetbl.insert_one(room)
        if len(roomlist)<120:
            break



def get_panda_all_info(game_channel):
    for page in range(1,10):
        cate=game_channel.split('/')[-1]
        url='http://www.panda.tv/ajax_sort?token=&pageno={}&pagenum=120&classification={}'.format(page,cate)

        wb_data=requests.get(url)
        # result=wb_data.text.encode('latin-1').decode('unicode_escape')
        wb=json.loads(wb_data.text)
        roomlist=wb['data']['items']
        for i in roomlist:
            ob_num=int(i['person_num'])
            if ob_num<5:
                break
            room_obs=i['person_num']
            room_title=i['name']
            room_url='http://www.panda.tv/'+i['id']
            room_owner=i['userinfo']['nickName']
            room_imgsrc=i['pictures']['img']
            room_pic='熊猫'+i['id']+'.jpg'
            room_tag=i['classification']['cname']

            room={
                'url':room_url,
                'data_from':'熊猫',
                'title':room_title,
                'owner':room_owner,
                'tag':room_tag,
                'obs':room_obs,
                'ob_num':ob_num,
                'on_off':1,
                'room_pic':room_pic,
                'room_imgsrc':room_imgsrc
            }
            livetbl.insert_one(room)
            # print(room)
        if len(roomlist)<120:
            break


def get_zhanqi_all_info(game_channel):
    gameid={
        'watch':'82',
        'how':'9',
        'hots':'21',
        'war3':'18',
        'sc2':'5'

    }

    # print(soup.select('#js-live-list-panel > div.tabc.active'))
    cate=game_channel.split('/')[-1]
    for page in range(1,10):
        url='http://www.zhanqi.tv/api/static/game.lives/{}/30-{}.json'.format(gameid[cate],str(page))
        wb_data=requests.get(url).text
        wb=json.loads(wb_data)
        roomlist=wb['data']['rooms']
        for i in roomlist:
            room_obs=i['online']
            ob_num=int(room_obs)
            if ob_num<5:
                break
            room_title=i['title']
            room_url='http://www.zhanqi.tv/'+i['code']
            room_owner=i['nickname']
            room_imgsrc=i['bpic'].strip('\'')
            room_pic='战旗'+i['code']+'.jpg'
            room_tag=i['gameName']

            room={
                'url':room_url,
                'data_from':'战旗',
                'title':room_title,
                'owner':room_owner,
                'tag':room_tag,
                'obs':room_obs,
                'ob_num':ob_num,
                'on_off':1,
                'room_pic':room_pic,
                'room_imgsrc':room_imgsrc
            }
            livetbl.insert_one(room)
            # print(room)
        if len(roomlist)<120:
            break
        # print(wb_data)




# init_crawl()
# a=get_douyu()
# if len(a):
#     print(a)
# else:
#     print('blocked')
# list(map(get_douyu_all_info, a))
# livelist=[i for i in livetbl.find()]
# pool = Pool()
# for i in livetbl.find():
#     pool.apply_async(downloadpic,args=(i['room_imgsrc'],i['room_pic']))
# pool.close()
# pool.join()
# for i in livetbl.find():
#     downloadpic(i['room_imgsrc'],i['room_pic'])
