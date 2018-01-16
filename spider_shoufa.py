# -*- coding:utf-8 -*-
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
            'User-Agent': 'Mozilla / 5.0(Windows NT 6.1;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 45.0.2454.101Safari / 537.36'
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
    spider_zhuanji()


def spider_zhuanji():
    page = 0
    # ids= []
    while page<=8:
        shoufa_url = "http://music.baidu.com/album/shoufa?order=time&style=all&start="+str(page*10)
        header = {
            "Host": "music.baidu.com",
            "User-Agent": ua_list.random
        }
        ip = choice(proxy_list)
        http = {"https": 'https://' + ip}
        response = requests.get(shoufa_url, headers=header, proxies=http).content
        html = etree.HTML(response)
        album_id = html.xpath("//ul/li/div[1]/div[2]/div[3]/a/@albumid")
        for id in album_id:
            print id
            # ids.append(id)
            spider_list(id)
        page+=1
    # print ids
    # print len(ids)
    # spider_list(ids)
def spider_list(id,file_path='shouf_img'):
    album_url = "http://music.baidu.com/album/" + id
    header = {
        "Host": "music.baidu.com",
        "User-Agent": ua_list.random
    }
    ip = choice(proxy_list)
    http = {"https": 'https://' + ip}
    response = requests.get(album_url, headers=header, proxies=http).content
    html = etree.HTML(response)
    img = html.xpath('//*[@id="cover"]/img/@src')
    # print img_url
    img_url = ''.join(img)  #原图
    print img_url
    img_url3 = re.findall(r'(.*)@s', img_url)
    img_url2 = ''.join(img_url3)
    big_img_url = img_url2 + "@s_1,w_834,h_834" #大图
    centre_img_url = img_url2 + "@s_1,w_188,h_188" #中图
    small_img_url = img_url2 + "@s_1,w_142,h_142" #小图
    print big_img_url
    print centre_img_url
    print small_img_url
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    try:
        if not os.path.exists(file_path):
            print '文件夹', file_path, '不存在，重新建立'
            # os.mkdir(file_path)
            os.makedirs(file_path)
        file_suffix = ''.join(re.findall(r'pic/(.*)@s', img_url)).split('/')[2] #本地路径
        print file_suffix
        # 拼接图片名（包含路径）
        filename = '{}{}{}'.format(file_path, os.sep, file_suffix)
        # 下载图片，并保存到文件夹中
        # filename =
        urllib.urlretrieve(img_url, filename=filename)
    except IOError as e:
        print '文件操作失败', e
    except Exception as e:
        print '错误 ：', e
    else:
        singer = html.xpath('//div[1]/div[2]/ul/li[1]/span/a/text()')  # 歌手
        if len(singer) == 0:
            singer = html.xpath('//div[1]/div[2]/ul/li[2]/span/a/text()')  # 歌手
            title = html.xpath('//div[1]/div[2]/h2/text()')  # 标题
            all = html.xpath('//div[1]/div[1]/div[1]/div[2]/ul/li[3]/text()')
            try:
                desc = html.xpath('//div/div[1]/div[1]/p/span[2]/text()')[0] # 描述
            except:
                desc = None
            singers = []
            for s in singer:
                singers.append(s)
            try:
                data_time = all[0].split()[0]
            except:

                album_time = None
                album_company = None
            else:
                album_time = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", data_time)  # 专辑发行时间
                a = len(album_time)
                if a == 0:
                    album_company = html.xpath("//div/div[1]/div[1]/div[2]/ul/li[2]/text()")[0][5:20]

                    album_time = []
                else:
                    album_time = album_time[0]
                    try:
                        album_company = all[0].split()[2]
                    except:
                        album_company = all[0].split()[1][5:30]
            print '111111111111111111'
            print title[0]
            print singer[0]
            print album_time
            print album_company
            print desc
            data_info = {
                "titleid": id,
                "title": title[0],
                "singer": singer[0],
                "album_time": album_time,
                "album_company": album_company,
                "desc": desc,
                "big_img_url": big_img_url,
                "centre_img_url": centre_img_url,
                "small_img_url": small_img_url,
                # "local_img":file_suffix,
            }
        else:
            title = html.xpath('//div/div[1]/div[1]/div[1]/div[2]/h2/text()')  # 标题
            all = html.xpath('//div/div[1]/div[1]/div[2]/ul/li[2]/text()')
            try:
                desc = html.xpath('//div[1]/div[1]/p/span[2]/text()')[0]  # 描述
            except:
                desc = None
            singers = []
            for s in singer:
                singers.append(s)
            try:
                data_time = all[0].split()[0]
            except:

                album_time = None
                album_company = None
            else:
                album_time = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", data_time)  # 专辑发行时间
                a = len(album_time)
                if a == 0:
                    album_company = html.xpath("//div/div[1]/div[1]/div[2]/ul/li[2]/text()")[0][5:20]

                    album_time = []
                else:
                    album_time = album_time[0]
                    # album_company = all[0].split()[1][5:20]
                    try:
                        album_company = all[0].split()[2]
                    except:
                        album_company = all[0].split()[1][5:30]
            print '111111111111111111'
            print title[0]
            print singers[0]
            print album_time
            print album_company
            print desc
            data_info = {
                "titleid": id,
                "title": title[0],
                "singer": singers[0],
                "album_time": album_time,
                "album_company": album_company,
                "desc": desc,
                "big_img_url": big_img_url,
                "centre_img_url": centre_img_url,
                "small_img_url": small_img_url,
                "local_img": file_suffix,
            }
            # client = pymongo.MongoClient('localhost', 27017)
            # db = client['shoufamusic']

        list = html.xpath('//div/div[1]/div[2]/div[2]/div/ul/li/@data-songitem')
        spider_song(list, id, data_info, album_time)

def spider_song(list,id,data_info,album_time,size=16, chars=string.ascii_letters + string.digits):
    client = pymongo.MongoClient('localhost', 27017)
    db = client['shoufamusic']
    dict = []
    for i in list:
        m = json.loads(i)
        sid = m['songItem']['sid']
        # print sid

        timeurl = "http://play.baidu.com/data/music/songlink?songIds=" + sid  # 歌曲播放时长爬取url
        try:
            header = {
                "Host": "music.baidu.com",
                "User-Agent": ua_list.random
            }
            ip = choice(proxy_list)
            http = {"https": 'https://' + ip}
            response = requests.get(timeurl, headers=header, proxies=http)
            js = response.json()
        except Exception, e:
            times=0
        else:
            time = js["data"]["songList"][0]["time"]  # 歌曲时长单位秒
            m, s = divmod(time, 60)
            h, m = divmod(m, 60)
            times = ("%02d:%02d" % (m, s))  # 歌曲时长转化分钟
        album_url = "http://music.baidu.com/song/" + sid
        header = {
            "Host": "music.baidu.com",
            "User-Agent": ua_list.random
        }
        ip = choice(proxy_list)
        http = {"https": 'https://' + ip}
        response = requests.get(album_url, headers=header, proxies=http).content
        html = etree.HTML(response)
        singers = html.xpath('//div[3]/ul/li[1]/span/a/text()')
        print len(singers)
        if len(singers) == 0:
            lrc = html.xpath('//div[2]/div[2]/div/@data-lrclink')
            if len(lrc)==0:
                lrc = None
            else:
                lrc = html.xpath('//div[2]/div[2]/div/@data-lrclink')

            name = html.xpath('//div[2]/div[1]/div/h2/span[1]/text()')
            singers2 = html.xpath('//div[3]/ul/li[2]/span/a/text()')
            s = []
            print singers2
            for i in singers2:
                s.append(i)
            album = html.xpath('//div[2]/div[3]/ul/li[3]/a/text()')
            a = ''.join(album)
            album = ''.join(a.split())
            singer = ''.join(s)
            print album
            print singer
            print name
            print lrc
            print times
            print album_time

        else:
            lrc = html.xpath('//div[2]/div[2]/div/@data-lrclink')
            if len(lrc) == 0:
                lrc = None
            else:
                lrc = html.xpath('//div[2]/div[2]/div/@data-lrclink')
            name = html.xpath('//div[2]/div[1]/div/h2/span[1]/text()')
            singers2 = html.xpath('//div[3]/ul/li[1]/span/a/text()')
            s = []
            for i in singers2:
                s.append(i)
            album = html.xpath('//div[3]/ul/li[2]/a/text()')
            a = ''.join(album)
            album = ''.join(a.split())
            singer = ''.join(s)
            print singers2
            print album
            print singer
            print name
            print lrc
            print times
            print album_time
        print '55555555555555'
        print singer
        print album_time
        try:
            name=name[0]
        except:
            name = None
        print '66666666666666666666'
        m = ''.join(random.choice(chars) for _ in range(size))  # 随机16位字符串
        apikey = "d3S3SbItdlYDj4KaOB1qIfuM"
        secret = "221b497771f29a469236d77cf5f376de"  # 密钥
        token = "c792044dac004a6c96a48............"  # 百度token
        st = m + apikey + secret + token  # 字符串拼接r
        sha = hashlib.sha1(st)
        encrypts = sha.hexdigest()
        sig = m + ":" + encrypts
        url = "https://openapi-iot.baidu.com/v1/music/query/singer?singer=" + singer +"&page=1&page_size=50"
        print '.......................................'
        print url
        my_headers = {
            "X-IOT-Signature": sig,
            "X-IOT-APP": apikey,
            "X-IOT-Token": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }

        html = requests.get(url, headers=my_headers)
        s = html.json()
        try:
            m = s["data"]["list"]
        except:
            pass
        else:
            print m
            for a in m:
                try:
                    if a['name'] == name and (a['publish_time'] == album_time or a['singer_name'] == [singer]):
                        imgurl = a["head_image_url"]

                        # local_img = ''.join(re.findall(r"c/(.*)@s", imgurl))
                        # if len(local_img) == 0:
                        #     local_img = ''.join(re.findall(r"http://(.*)", imgurl))
                        # else:
                        #     local_img = ''.join(re.findall(r"c/(.*)@s", imgurl))
                        publish_time = a['publish_time']
                        id2 = a["id"]
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

                        name2 = a['name']
                        singer_name = a['singer_name'][0]

                        data1 = {
                            "name_id":id2,
                            "album": album,
                            "singer": singer_name,
                            "name": name2,
                            "lrc": ''.join(lrc),
                            "time": times,
                            "publish_time":publish_time,
                            "album_time": album_time,
                            "big_imgurl":big_imgurl,
                            "img_url":img_url,
                            "small_url":small_url
                        }

                        print data1
                        dict.append(data1)

                        msg3 = db['songlist_info']
                        msg3.insert(data1)

                except  Exception, e:
                    print e
    number=len(dict)
    data = {
        "title_id":id,
        "song_number":number,
        "info":data_info,
        "list":dict
    }

    msg1 = db['shoufa']
    msg1.insert(data_info)
    msg2 = db['songlist']
    msg2.insert(data)

    print dict
    print len(dict)
    if len(dict)<1:

        idm = str(id)
        id3 = db.shoufa.find_one({'titleid': idm})['_id']
        id4 = db.songlist.find_one({'title_id': idm})['_id']
        db.shoufa.remove(id3)
        db.songlist.remove(id4)


if __name__ == '__main__':
    get_ip(1)