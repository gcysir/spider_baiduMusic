# -*- coding:utf-8 -*-
# @Time     :2018-01-09
# @Author   :gcy
# @Email    :
# @File     :
import requests
import os
import sys
import random
import re
import json
import string
import urllib
import hashlib
import pymongo
from lxml import etree
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from random import choice
reload(sys)
sys.setdefaultencoding('utf-8')

# print(sys.getdefaultencoding())
ua_list = UserAgent()


proxy_list = []
def get_ip(numpage):
    '''获取代理IP'''
    for num in xrange(1, numpage + 1):
        url = "http://www.xicidaili.com/wn/"
        # url = 'http://www.xicidaili.com/nn'
        my_headers = {
            'Accept': 'text/html, application/xhtml+xml, application/xml;',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Referer': 'http: // www.xicidaili.com/nn',
            "User-Agent": ua_list.random
        }
        r = requests.get(url,headers=my_headers)
        soup = BeautifulSoup(r.text,'html.parser')
        data = soup.find_all('td')

        #定义IP和端口Pattern规则
        ip_compile = re.compile(r'<td>(\d+\.\d+\.\d+\.\d+)</td>')  #匹配IP
        port_compile = re.compile(r'<td>(\d+)</td>')  #匹配端口
        ips = re.findall(ip_compile,str(data))    #获取所有IP
        ports = re.findall(port_compile,str(data))  #获取所有端口
        # z = [':'.join(i) for i in zip(ip,port)]  #列表生成式
        for (ip,port) in zip(ips,ports):
            ip = ''.join(ip)+":"+''.join(port)
            http={"https": 'https://' + ip}
            url="http://ip.chinaz.com/getip.aspx"
            try:
                response = requests.get(url,proxies=http)
            except Exception,e:
                print e
            else:
                proxy_list.append(ip)
                print ip
    spider_id()

def spider_id(file_path='hot_img'):
    page=0
    while page<=10:
        client = pymongo.MongoClient('localhost',27017)
        db = client['appmusic']
        msg = db['hot_music']
        header={
            "Host": "music.baidu.com",
            "User-Agent":ua_list.random
        }
        ip = choice(proxy_list)
        http = {"https": 'https://' + ip}
        url = "http://music.baidu.com/songlist/tag/全部?orderType=1&offset="+str(page*20)
        try:
            html = requests.get(url,headers=header,proxies=http,timeout=30).content
            h = etree.HTML(html)
        except:
            pass
        imgurls = h.xpath('//li/div/img/@src') #图片地址
        listens = h.xpath('//li/div/div[1]/span/text()') #播放量
        titles = h.xpath('//ul/li/p[1]/a/text()') #标题
        titleids = h.xpath('//ul//div/div[2]/a[2]/@data-listid') #标题id
        bys = h.xpath('//ul//p[2]/a/text()')
        for (imgurl,listen,title,titleid,by) in zip(imgurls,listens,titles,titleids,bys):
            print '开始存储。。。。。。。。。。'

            # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
            try:
                if not os.path.exists(file_path):
                    print '文件夹', file_path, '不存在，重新建立'
                    # os.mkdir(file_path)
                    os.makedirs(file_path)
                # 获得图片后缀
                file_suffix = ''.join(re.findall(r'pic/(.*)', imgurl))

                print file_suffix
                # 拼接图片名（包含路径）
                filename = '{}{}{}'.format(file_path, os.sep, file_suffix)
                # 下载图片，并保存到文件夹中
                urllib.urlretrieve(imgurl, filename=filename)
            except IOError as e:
                print '文件操作失败', e
            except Exception as e:
                print '错误 ：', e
            else:
                url = "http://music.baidu.com/songlist/" + titleid
                header = {
                    "Host": "music.baidu.com",
                    "User-Agent": ua_list.random
                }
                ip = choice(proxy_list)
                http = {"https": 'https://' + ip}
                try:
                    html = requests.get(url, headers=header, proxies=http,timeout=30).content
                    h = etree.HTML(html)
                except:
                    pass
                byimgurl = h.xpath('//div[2]/div[2]/div[1]/a[1]/img/@src')  # by头像
                tg = h.xpath('//div[2]/div[1]/div/div[2]/div[2]/div[2]/a/text()')  # tag
                print len(tg)
                tag = []
                for i in tg:
                    tag.append(i)
                song_introduction = h.xpath('//div[1]/div/div[4]/span[2]/text()')  # 歌曲简介
                # number = h.xpath('//span[@class="songlist-num fl f14 c9"]/text()')  # 歌曲数量
                play = h.xpath('//span[@class="songlist-listen f14 c9"]/text()')  # 播放次数
                a = ''.join(play)

                playnumbers = re.sub("\D", "", a)
                # playnumber =int(playnumbers)
                big_imgurl = imgurl+"@s_1,w_834,h_834"
                img_url = imgurl+'@s_1,w_188,h_188'
                small_url = imgurl+'@s_1,w_142,h_142'
                data = {
                    "img_url": img_url,
                    "bigimg":big_imgurl,
                    "smallimg":small_url,
                    "listen": listen.strip(),
                    "title": title,
                    "by": by,
                    "filename": file_suffix,
                    'byimgurl': ''.join(byimgurl),
                    'tag': tag,
                    'songintroduction': ''.join(song_introduction),
                    'songid': titleid,
                    'playnumber': playnumbers
                }
                print data
                msg.insert(data)

                print '存储结束。。。。。。。'
                spider_info(titleid)

        page += 1


def spider_info(id2,size=16, chars=string.ascii_letters + string.digits):
    client = pymongo.MongoClient('localhost', 27017)
    db = client['appmusic']

    url = "http://music.baidu.com/songlist/"+id2
    header = {
        "Host": "music.baidu.com",
        "User-Agent": ua_list.random
    }
    ip = choice(proxy_list)
    http = {"https": 'https://' + ip}
    try:
        html = requests.get(url, headers=header, proxies=http,timeout=30).content
        h = etree.HTML(html)
    except:
        pass
    imgurl = h.xpath('//div[2]/div[1]/div/div[2]/div[1]/a/img/@src') #图片url
    title = h.xpath('//div/div[2]/div[2]/h1/text()') #标题
    by = h.xpath('//div/div[2]/div[2]/div[1]/a[2]/text()') #by
    byimgurl = h.xpath('//div[2]/div[2]/div[1]/a[1]/img/@src') #by头像
    tg = h.xpath('//div[2]/div[1]/div/div[2]/div[2]/div[2]/a/text()') #tag
    tag2 = []
    for i in tg:
        tag2.append(i)
    song_introduction = h.xpath('//div[1]/div/div[4]/span[2]/text()') #歌曲简介
    play = h.xpath('//span[@class="songlist-listen f14 c9"]/text()') #播放次数
    a = ''.join(play)

    playnumber = re.sub("\D", "", a)
    big_imgurl = ''.join(imgurl)+"@s_1,w_834,h_834" #大图
    img_url = ''.join(imgurl)+'@s_1,w_188,h_188' #中图
    small_url = ''.join(imgurl)+'@s_1,w_142,h_142' # 小图

    indexs = h.xpath('//ul/li/div/span[1]/text()') #序号
    songs = h.xpath('//ul/li/div/span[3]/a[1]/text()') #歌曲名
    ids = h.xpath('//ul/li/div/span[2]/span/@data-musicicon') #歌曲id
    albums = h.xpath('//ul/li/div/span[5]/a/@title') #专辑
    singers = h.xpath('//ul/li/div/span[4]/span/@title') #歌手
    dict=[]
    for (index,song,album,singer,id) in zip(indexs,songs,albums,singers,ids):
        m=json.loads(id)
        songid = m["id"] #歌曲id
        albumid = m['albumId']  # 专辑id
        header = {
            "User-Agent": ua_list.random
        }
        ip = choice(proxy_list)
        http = {"https": 'https://' + ip}
        tagurl = "http://music.baidu.com/song/" + songid
        try:
            response = requests.get(tagurl,headers=header,proxies=http,timeout=30).content
        except Exception,e:
            print e
            continue

        h = etree.HTML(response)
        tg = h.xpath("//div[1]/div[2]/div[3]/ul/li[4]/a/text()")
        if len(tg)==0:
            tg = h.xpath('//div[2]/div[3]/ul/li[3]/a/text()')
        tag1 = []
        for i in tg:
            tag1.append(i)
        timeurl = "http://play.baidu.com/data/music/songlink?songIds="+songid  #歌曲播放时长爬取url
        # response = requests.get(timeurl,headers=header)
        try:
            ip = choice(proxy_list)
            http = {"https": 'https://' + ip}
            response = requests.get(timeurl, headers=header,proxies=http,timeout=30)
            js = response.json()
        except Exception,e:
            pass
        else:
            time = js["data"]["songList"][0]["time"] #歌曲时长单位秒
            m, s = divmod(time, 60)
            h, m = divmod(m, 60)
            times = ("%02d:%02d" % (m, s)) #歌曲时长转化分钟

        if albumid!=0:
            header = {

                "User-Agent": ua_list.random
            }
            album_url = "http://music.baidu.com/album/" + albumid
            ip = choice(proxy_list)
            http = {"https": 'https://' + ip}
            try:
                response = requests.get(album_url,headers=header,proxies=http).content
                html = etree.HTML(response)
            except Exception,e:
                pass
            s_singer=html.xpath('//div[1]/div[1]/div[1]/div[2]/ul/li[2]/span/a')
            if len(s_singer)==0:
                time = html.xpath("//div[4]/div/div[1]/div[1]/div[1]/div[2]/ul/li[2]/text()")  # 专辑发布时间及公司
                try:
                    tag = html.xpath("//div[4]/div/div[1]/div[1]/div[1]/div[2]/ul/li[3]/text()")[0][3:20]  # 专辑流派
                except:
                    tag=[]

                try:
                    data_time = time[0].split()[0]
                except:
                    album_time = None
                    album_company = None
                else:
                    album_time = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", data_time)  # 专辑发行时间

                    if len(album_time) == 0:
                        # 发行公司
                        album_company = html.xpath("//div[4]/div/div[1]/div[1]/div[1]/div[2]/ul/li[2]/text()")[0][5:20]
                        album_time = []
                    else:
                        album_time = album_time[0]
                        try:
                            album_company = time[0].split()[1][5:20]
                        except:
                            album_company = None
            else:
                time = html.xpath("//div/div[1]/div[1]/div[1]/div[2]/ul/li[3]/text()")  # 专辑发布时间及公司
                try:
                    tag = html.xpath('//div/div[1]/div[1]/div[1]/div[2]/ul/li[4]/text()')[0][3:20] # 专辑流派

                except:
                    tag=[]
                try:
                    data_time = time[0].split()[0]
                except:
                    album_time = None
                    album_company = None
                else:
                    album_time = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", data_time)  # 专辑发行时间

                    if len(album_time) == 0:
                        # 发行公司
                        album_company = html.xpath("//div[4]/div/div[1]/div[1]/div[1]/div[2]/ul/li[2]/text()")[0][5:20]
                        album_time = []
                    else:
                        album_time = album_time[0]
                        try:
                            album_company = time[0].split()[1][5:20]
                        except:
                            album_company = None
        else:
            album_time = None
            album_company = None
            tag = None
        # 通过获取到的歌名歌手爬取可用接口歌曲信息
        # 公司内部接口不便外用
        m = ''.join(random.choice(chars) for _ in range(size))  # 随机16位字符串
        apikey = "d3S3SbItdlYDj4KaOB1qIfuM"
        secret = "221b497771f29a469236d77cf5f376de"  # 密钥
        token = "c792044dac004a6c96a486280........"  # 百度token
        st = m + apikey + secret + token  # 字符串拼接r
        sha = hashlib.sha1(st)
        encrypts = sha.hexdigest()
        sig = m + ":" + encrypts
        url = "https://openapi-iot.baidu.com/v1/music/query/singer?singer="+ singer + "&page=1&page_size=50"
        my_headers = {
            "X-IOT-Signature": sig,
            "X-IOT-APP": apikey,
            "X-IOT-Token": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }
        try:
            html = requests.get(url, headers=my_headers,timeout=30)
            s = html.json()
            print s
            m = s["data"]["list"]
        except Exception,e:
            pass
        else:

            for a in m:
                try:
                    if a['name'] == song and (a['publish_time']==album_time or a['singer_name']==[singer]):
                        imgurl = a["head_image_url"]

                        # local_img = ''.join(re.findall(r"c/(.*)@s", imgurl))
                        # if len(local_img)==0:
                        #     local_img=''.join(re.findall(r"http://(.*)", imgurl))
                        # else:
                        #     local_img = ''.join(re.findall(r"c/(.*)@s", imgurl))
                        publish_time = a['publish_time']
                        id = a["id"]
                        url = re.findall(r"(.*)@s", imgurl)
                        if len(url) == 0:
                            url = imgurl
                            big_imgurl = url
                            img_url = url
                            small_url = url
                        else:
                            url = url
                            big_imgurl = ''.join(url) + "@s_1,w_834,h_834"
                            img_url = ''.join(url) + '@s_1,w_188,h_188'
                            small_url = ''.join(url) + '@s_1,w_142,h_142'

                        name = a['name']
                        singer_name = a['singer_name'][0]
                        print big_imgurl
                        print img_url
                        print small_url
                        print id
                        print publish_time
                        print name
                        print singer_name
                        # print local_img
                        print albumid
                        print album
                        data2 = {
                            "index": index,
                            "name": name,
                            "singer_name": singer_name,
                            "songid": id,
                            "times": times,
                            "publish_time": ''.join(publish_time),
                            # "local_img": local_img,
                            "songimgurl": img_url,
                            "bigsongimgurl": big_imgurl,
                            "smallsongimgurl": small_url,
                            "album": album,
                            "album_id": albumid,
                            "album_company": "".join(album_company),
                            "album_time": "".join(album_time),
                            "album_tag":''.join(tag),
                            "song_tag":tag1,

                        }
                        dict.append(data2)
                        data3 = {
                            "name": name,
                            "singer_name": singer_name,
                            "songid": id,
                            "times": times,
                            "publish_time": ''.join(publish_time),
                            # "local_img": local_img,
                            "songimgurl": img_url,
                            "bigsongimgurl": big_imgurl,
                            "smallsongimgurl": small_url,
                            "album": album,
                            "album_id": albumid,
                            "album_company": "".join(album_company),
                            "album_time": "".join(album_time),
                            "album_tag": ''.join(tag),
                            "song_tag": tag1,
                        }

                        msg = db['hot_songlist']
                        msg.insert(data3)
                except  Exception,e:
                    print e
                    # id_generator(song,singer)
    number = len(dict)
    data1 = {
        "img_url": img_url,
        "bigimg": big_imgurl,
        "smallimg": small_url,
        'title': ''.join(title),
        'by': ''.join(by),
        'byimgurl': ''.join(byimgurl),
        'tag': tag2,
        'titleintroduction': ''.join(song_introduction),
        # 'titleid':''.join(id2),
        'titleid': id2,
        'titlenumber': number,
        'playnumber': playnumber
    }

    data={
        'titleid':id2,
        "info":data1,
        "list":dict
    }
    ms = db['hot_singleinfo']
    ms.insert(data)
    if len(dict) < 1:
        idm = str(id2)
        id3 = db.hot_music.find_one({'songid':idm})['_id']
        id4 = db.hot_singleinfo.find_one({'titleid': idm})['_id']
        db.hot_music.remove(id3)
        db.hot_singleinfo.remove(id4)
if __name__ == '__main__':
    get_ip(1)
    # spider_id()