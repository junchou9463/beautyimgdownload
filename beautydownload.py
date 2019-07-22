# -*- coding:utf-8 -*-
# Author:Jun

import requests
import os
from lxml import etree
from threading import *
from time import sleep
from bs4 import BeautifulSoup


nMaxThread = 3  # 这里设置需要开启几条线程
ThreadLock = BoundedSemaphore(nMaxThread)
path = 'D:/meizitu/'
gHeads = {
    'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
}
Hostreferer = {
    'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer':'http://www.mzitu.com'
               }
Picreferer = {
    'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer':'http://i.meizitu.net'
}

class Meizitu(Thread):
    def __init__(self, mainReferer, url, title,pic_max):
        Thread.__init__(self)
        self.MainReferer = mainReferer
        self.url = url
        self.title = title  # 这里是为了把<b></b>给删除
        self.pic_max = pic_max


    def run(self):
        try:

            self.SavePath()

        finally:
            ThreadLock.release()

    def GetPhotoUrl(self):
        heads = {
            "Referer": self.MainReferer
        }
        heads.update(gHeads)
        html = requests.get(self.url, headers=heads)
        if html.status_code == 200:
            xmlContent = etree.HTML(html.text)
            urlList = xmlContent.xpath("//div[@id='picture']/p/img/@src")
            return urlList
        else:
            return None

    def SavePath(self):
        heads = {
            "Referer": self.MainReferer
        }
        heads.update(gHeads)
        href = self.url
        html = requests.get(href, headers=heads)
        mess = BeautifulSoup(html.text, "html.parser")
        pic_max_list = mess.find_all('span')
        # print(pic_max)
        try:
            pic_max = pic_max_list[9].text  # 最大页数
        except:
            pic_max = 10  # 最大页数
        for num in range(1, int(pic_max) + 1):
            j = 0
            while j < 5:
                try:
                    pic = self.url + '/' + str(num)
                    html_1 = requests.get(pic, headers=heads)
                    # xmlContent = etree.HTML(html_1.content)
                    # hrefsrc = xmlContent.xpath("//div[@class='main-image']/p/a/img/@src")
                    # # print(hrefsrc)
                    # file_name = hrefsrc[0].split(r'/')[-1]
                    # html = requests.get(hrefsrc[0], headers=Picreferer)
                    mess = BeautifulSoup(html_1.text, "html.parser")
                    pic_url = mess.find('img', alt=self.title)
                    html = requests.get(pic_url['src'], headers=heads)
                    file_name = pic_url['src'].split(r'/')[-1]
                except :
                    continue
                if html.status_code == 200:
                    f = open(file_name, 'wb')
                    f.write(html.content)
                    f.close()
                    break
                elif html.status_code == 404:
                    j += 1
                    sleep(0.05)
                    continue
                else:
                    return None


def main():

    all_url = 'https://www.mzitu.com/tag/youhuo/'
    start_html = requests.get(all_url, headers=Hostreferer)

    # 保存地址

    # 找寻最大页数
    soup = BeautifulSoup(start_html.text, "html.parser")
    page = soup.find_all('a', class_='page-numbers')
    max_page = page[-2].text
    print(max_page)
    for i in range(2,int(max_page)+1):
        url = "https://www.mzitu.com/tag/youhuo/page/%s/" % (i)
        html = requests.get(url, headers=Hostreferer)
        if html.status_code == 200:
            xmlContent = etree.HTML(html.content)
            hrefList = xmlContent.xpath("//div[@class='postlist']/ul/li/a/@href")
            titleList = xmlContent.xpath("//div[@class='postlist']/ul/li/a/img/@alt")
            print(titleList)
            for i in range(len(hrefList)):
                print("准备扒取：" + titleList[i])
                if (os.path.exists(path + titleList[i].strip().replace('?', '').replace(':', ''))):
                    # print('目录已存在')
                    flag = 1
                else:
                    os.makedirs(path + titleList[i].strip().replace('?', '').replace(':', ''))
                    flag = 0
                os.chdir(path + titleList[i].strip().replace('?', '').replace(':', ''))
                href = hrefList[i]
                html = requests.get(href, headers=Hostreferer)
                mess = BeautifulSoup(html.text, "html.parser")
                pic_max_list = mess.find_all('span')
                # print(pic_max)
                try:
                    pic_max = pic_max_list[9].text  # 最大页数
                except:
                    pic_max = 10 # 最大页数
                print(pic_max)
                if (flag == 1 and len(os.listdir(path + titleList[i].strip().replace('?', '').replace(':', ''))) >= int(
                        pic_max)):
                    print('已经保存完毕，跳过')
                    continue
                ThreadLock.acquire()
                t = Meizitu(url, hrefList[i], titleList[i],pic_max)
                t.start()


if __name__ == '__main__':
    main()
