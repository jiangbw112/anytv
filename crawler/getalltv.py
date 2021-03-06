from bs4 import BeautifulSoup
import requests
import re
import pymongo
import os
from shutil import rmtree
import multiprocessing
import random
import json
import string

resp = requests.get("http://tor1024.com/static/proxy_pool.txt")
ips_txt = resp.text.strip().split("\n")
proxy_list = []
for i in ips_txt:
    try:
        k = json.loads(i)
        proxy_list.append(k)
    except Exception as e:
        print(e)

# proxies = random.choice(proxy_list) # 随机获取代理ip



tv_cate={'war3':'魔兽争霸','overwatch':'守望先锋','sc2':'星际争霸','hots':'风暴英雄','how':'炉石传说'}

client = pymongo.MongoClient('localhost', 27017)
maintbl=client['maintbl']
livetbl=maintbl['livetbl']
# livetbl.remove()


def init_crawl():
    livetbl.remove()
    path='../web/anytv/static/images/room_img/'
    if os.path.isdir(path):
        rmtree(path)
    os.mkdir(path)

def downloadpic(url,filename):
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
    r=requests.get(url,proxies=proxies)
    if r.status_code!=200:
        return
    room_img_path='../web/anytv/static/images/room_img/'
    target=room_img_path+filename
    with open(target,'wb') as fs:
        fs.write(r.content)



def get_douyu():
    url ='http://www.douyu.com/directory'
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
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
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
    wb_data = requests.get(url,proxies=proxies)
    wb_data.encoding='utf-8'
    soup=BeautifulSoup(wb_data.text,'lxml')

    panda_channels=soup.select('li a.video-list-item-wrap')

    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in panda_channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append('http://www.panda.tv'+i.get('href'))
    return gamelist

def get_zhanqi():
    url='http://www.zhanqi.tv/games'
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
    wb_data = requests.get(url,proxies=proxies)
    wb_data.encoding='utf-8'
    soup=BeautifulSoup(wb_data.text,'lxml')

    channels=soup.select('#game-list-panel li div a')
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append('http://www.zhanqi.tv'+i.get('href'))
    return gamelist

def get_huya():
    url='http://www.huya.com/g'
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
    wb_data = requests.get(url,proxies=proxies)
    soup=BeautifulSoup(wb_data.text,'lxml')

    channels=soup.select('a.pic.clickstat')
    gamelist=[]
    patten=re.compile('|'.join(tv_cate.values()))
    for i in channels:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(str(i))):
                gamelist.append(i.get('href'))
    return gamelist


def get_quanmin():
    global proxy_list
    proxies = random.choice(proxy_list) # 随机获取代理ip
    wb_data = requests.get('http://www.quanmin.tv/json/categories/list.json',proxies=proxies).text
    wb=json.loads(wb_data)

    patten=re.compile('|'.join(tv_cate.values()))
    gamelist=[]
    for i in wb:
        if not len(gamelist)==len(tv_cate):
            if(patten.search(i['name'])):
                gamelist.append('http://www.quanmin.tv/game/'+i['slug'])
    return gamelist


def get_douyu_all_info(game_channel):
    global proxy_list
    for page in range(1,20):
        url=game_channel+'?page={}&isAjax=1'.format(str(page))
        proxies = random.choice(proxy_list) # 随机获取代理ip
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
    cate=game_channel.split('/')[-1]
    global proxy_list
    for page in range(1,20):
        url='http://www.panda.tv/ajax_sort?token=&pageno={}&pagenum=120&classification={}'.format(page,cate)
        proxies = random.choice(proxy_list) # 随机获取代理ip
        wb_data=requests.get(url,proxies=proxies)
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
    global proxy_list
    # print(soup.select('#js-live-list-panel > div.tabc.active'))
    cate=game_channel.split('/')[-1]
    for page in range(1,10):
        proxies = random.choice(proxy_list) # 随机获取代理ip
        url='http://www.zhanqi.tv/api/static/game.lives/{}/30-{}.json'.format(gameid[cate],str(page))
        wb_data=requests.get(url,proxies=proxies).text
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
            room_imgsrc=i['bpic']
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
        if len(roomlist)<30:
            break
        # print(wb_data)


def get_huya_all_info(game_channel):
    cate=requests.get(game_channel).text
    patten=re.compile(r'(GID\s=\s)(.+);')
    gameid = patten.search(cate).group(2).strip(' \'')
    global proxy_list
    for page in range(1,20):
        url='http://www.huya.com/index.php?m=Game&do=ajaxGameLiveByPage&gid={}&page={}&pageNum=1'.format(gameid,str(page))
        proxies = random.choice(proxy_list) # 随机获取代理ip
        wb_data=requests.get(url,proxies=proxies).text
        wb=json.loads(wb_data)
        roomlist=wb['data']['list']
        for i in roomlist:
            room_obs=i['totalCount']
            ob_num=int(room_obs)
            if ob_num<5:
                break
            room_title=i['introduction']
            room_url='http://www.huya.com/'+i['privateHost']
            room_owner=i['nick']
            room_imgsrc=i['screenshot'].strip('\'')
            room_pic='虎牙'+i['privateHost']+'.jpg'
            room_tag=i['gameFullName']

            room={
                'url':room_url,
                'data_from':'虎牙',
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
        if len(roomlist)<20:
            break


def get_quanmin_all_info(game_channel):
    cate=game_channel.split('/')[-1]
    global proxy_list
    for page in range(1,20):
        if page==1:
            url='http://www.quanmin.tv/json/categories/{}/list.json'.format(cate)
        else:
            url='http://www.quanmin.tv/json/categories/{}/list_{}.json'.format(cate,str(page))
        proxies = random.choice(proxy_list) # 随机获取代理ip
        wb_data=requests.get(url,proxies=proxies)
        # result=wb_data.text.encode('latin-1').decode('unicode_escape')
        wb=json.loads(wb_data.text)

        roomlist=wb['data']
        for i in roomlist:
            ob_num=int(i['view'])
            if ob_num<5:
                break
            room_obs=i['view']
            room_title=i['title']
            room_url='http://www.quanmin.tv/v/'+i['uid']
            room_owner=i['nick']
            room_imgsrc=i['thumb']
            room_pic='全民'+i['uid']+'.jpg'
            room_tag=i['category_name']

            room={
                'url':room_url,
                'data_from':'全民',
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
        if len(roomlist)<90:
            break






#
#
#


