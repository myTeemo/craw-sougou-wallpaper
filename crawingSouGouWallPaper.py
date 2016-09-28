#-*-coding:utf-8-*-

import sys
import requests
from lxml import etree
import json

reload(sys)
sys.setdefaultencoding('utf-8')

def get_page():

    startUrl = 'http://bizhi.sogou.com/cate/wplist'

    html = requests.get(startUrl,timeout=10)
    selector = etree.HTML(html.text)
    selectPictures = selector.xpath('//div[@class="wallpaper_dis"]/a/img/@src')  #选取打开网页上的图片,没有加载的
    selectNextJson = selector.xpath('//script[@type="text/javascript"]/text()')  #获取下个动态加载包的名称,

    basePictureurl,getNextJsonPackage = getresentPagePictures(selectPictures, selectNextJson)   #获取初始页的图片,并返回图片的固定基址和接下来的Json包

    getOtherPickages(basePictureurl, getNextJsonPackage)

def getresentPagePictures(selectPictures,selectNextJson):

    basePictureurl = ''

    for picture in selectPictures:
        basePictureurl = picture.split('_')[0]
        pictureName = picture.split('_')[0] + '.jpg'  # http://img01.sogoucdn.com/app/a/100540002//1544017_s_90_2_219x160.jpg
                                                      # http://img01.sogoucdn.com/app/a/100540002/1544017.jpg
        html = requests.get(pictureName, timeout=10)
        if html.status_code != '200':
            # print picture.split('_')[0].split('/')[-1]

            pictureName = 'http://bizhi.sogou.com/detail/info/' + picture.split('_')[0].split('/')[-1]
            html = requests.get(pictureName, timeout=10)
            selector = etree.HTML(html.text)
            pictureName = selector.xpath('//div[@class="unews_wp_big"]/img/@src')
            html = requests.get(pictureName[0], timeout=10)
            pictureName = pictureName[0]

        with open('picture/' + pictureName.split('/')[-1], 'wb') as f:
            print '正在保存:' + pictureName.split('/')[-1]
            f.write(html.content)  # 保存当前页的图片数据

    # < scrip type = "text/javascript" >
    # var min_wp_id = 1406625;   # 需要获取1406625
    getNextJsonPackage = selectNextJson[0].split(';')[0].split(' ')[-1]  # 取到 1406625

    basePictureurl = basePictureurl.split('/')[:-2]
    basePictureurl = '/'.join(basePictureurl) + '/'  # 取到Json包中图片数据的基址,因为数据包中并没有给出图片的完整地址

    return basePictureurl,getNextJsonPackage

def getOtherPickages(basePictureurl,getNextJsonPackage):
    time = 0;  # 定一个加载次数
    while time <= 5:
        time += 1
        print '\n第{}次加载数据:'.format(time)

        NewUrl = 'http://bizhi.sogou.com/cate/getCate/0/' + getNextJsonPackage  # Json 包地址

        jsonPackage = requests.get(NewUrl)
        jsonPackage = json.loads(jsonPackage.content)  # json库解析json数据包

        getNextJsonPackage = jsonPackage['min_wp_id']  # 获取到下一个Json数据包

        for id in jsonPackage['wallpapers']:
            newPictureUrl = basePictureurl + id['wp_id'] + '.jpg'
            html = requests.get(newPictureUrl, timeout=10)
            if html.status_code != '200':
                newPictureUrl = 'http://bizhi.sogou.com/detail/info/' + id['wp_id']
                html = requests.get(newPictureUrl, timeout=10)

                selector = etree.HTML(html.text)
                pictureName = selector.xpath('//div[@class="unews_wp_big"]/img/@src')
                html = requests.get(pictureName[0], timeout=10)

            with open('picture/' + id['wp_id'] + '.jpg', 'wb') as f:
                print '正在保存:' + id['wp_id'] + '.jpg'
                f.write(html.content)
    return

if __name__ == '__main__':
    get_page()

#爬虫的运行还与网络连接有关,如果发送请求的时候服务器响应的时间过长可能导致爬虫中断,数据采集不下来。
#
# Traceback (most recent call last):
#   File "/Users/Eilene/PycharmProjects/sougou_wallpaper/crawingSouGouWallPaper.py", line 49, in <module>
#     get_page()
#   File "/Users/Eilene/PycharmProjects/sougou_wallpaper/crawingSouGouWallPaper.py", line 44, in get_page
#     f.write(requests.get(newPictureUrl).content)
#   File "/Library/Python/2.7/site-packages/requests/api.py", line 70, in get
#     return request('get', url, params=params, **kwargs)
#   File "/Library/Python/2.7/site-packages/requests/api.py", line 56, in request
#     return session.request(method=method, url=url, **kwargs)
#   File "/Library/Python/2.7/site-packages/requests/sessions.py", line 475, in request
#     resp = self.send(prep, **send_kwargs)
#   File "/Library/Python/2.7/site-packages/requests/sessions.py", line 596, in send
#     r = adapter.send(request, **kwargs)
#   File "/Library/Python/2.7/site-packages/requests/adapters.py", line 473, in send
#     raise ConnectionError(err, request=request)
# requests.exceptions.ConnectionError: ('Connection aborted.', error(54, 'Connection reset by peer'))
# 常出现的Connection reset by peer: 原因可能是多方面的，不过更常见的原因是：
# ①：服务器的并发连接数超过了其承载量，服务器会将其中一些连接Down掉；
# ②：客户关掉了浏览器，而服务器还在给客户端发送数据；
# ③：浏览器端按了Stop