# -*- coding:utf-8 -*-
#created by zfq
#first edited: 2016.12.09

import requests
import re
import os
from bs4 import BeautifulSoup

s = requests.Session()
class Pixiv:
    
    def __init__(self):
        self.baseUrl = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.LoginUrl = "https://accounts.pixiv.net/api/login?lang=zh"
        self.loginHeader = {  
        'Host': "accounts.pixiv.net",  
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",  
        'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Connection': "keep-alive"
        }  
        self.return_to = "http://www.pixiv.net/"  
        self.pixiv_id = '773974336@qq.com',
        self.password = 'qss940107'
        self.postKey = []
        self.savedUrlList = []  #存放存储过的图片的url
        
    #获取此次session的post_key
    def getPostKeyAndCookie(self):
        loginHtml = s.get(self.baseUrl)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, loginHtml.text)
        self.postKey = result.group(1)
        loginData = {"pixiv_id": self.pixiv_id, "password": self.password, 'post_key': self.postKey, 'return_to': self.return_to} 
        s.post(self.LoginUrl, data = loginData, headers = self.loginHeader)

    #获取页面
    def getPageWithUrl(self, url):
        return s.get(url).text
    
    #输入文件夹名，创建文件夹
    def mkdir(self, path, folderName): 
        folderName = folderName.strip()
        isExists = os.path.exists(os.path.join(path, folderName))
        if not isExists:
            os.makedirs(os.path.join(path, folderName))
            print '建了一个名字叫做' + folderName + '的文件夹！'
            os.chdir(self.tag)  #切换到目录
            self.rootPath = os.getcwd()
            print self.rootPath
            os.makedirs(os.path.join(self.rootPath, "1-50"))
            os.makedirs(os.path.join(self.rootPath, "51-300"))
            os.makedirs(os.path.join(self.rootPath, "301-1000"))
            os.makedirs(os.path.join(self.rootPath, "1000以上"))
            print '在' + folderName + '文件夹下建立了 1-50 51-300 301-1000 1000以上 4个文件夹'
            return True
        else:
            print '名字叫做' + folderName + '的文件夹已经存在了！'
            os.chdir(self.tag)  #切换到目录
            self.rootPath = os.getcwd()
           
    #下载指定url的图片
    def getBigImg(self, sourceUrl, wholePageUrl, name):
        header = {
            'Referer': wholePageUrl,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
        }
        if sourceUrl in self.savedUrlList:
            print '该图片已经存在，不用再次保存，跳过！'
        else:
            self.savedUrlList.append(sourceUrl)
            imgExist = os.path.exists(os.getcwd() + '/' + name.encode('utf-8') + '.jpg')  #如果存在重名的，则给name加1重新命名
            if (imgExist):
                name = name + 're'
                print u'存在重名图片，重新命名为: ' + name
            suffixPattern = re.compile('.((\w){3})\Z')
            suffix = re.search(suffixPattern, sourceUrl)     #获取文件后缀，png或jpg
            img = s.get(sourceUrl, headers = header)
            f = open(name + '.' + suffix.group(1), 'wb') #写入多媒体文件要b这个参数
            f.write(img.content)  #多媒体文件要是用conctent！
            f.close()

    def getImg(self, url):
        #查找本页面内最大分辨率的图片的url的正则表达式
        singleImgePattern = re.compile('<div class="_illust_modal.*?<img alt="(.*?)".*?data-src="(.*?)".*?</div>', re.S)
        wholePageUrl = 'http://www.pixiv.net' + str(url)
        pageHtml = self.getPageWithUrl(wholePageUrl)
        singleImgResult = re.search(singleImgePattern, pageHtml)     #如果这个页面只有一张图片，那就返回那张图片的url和名字，如果是多张图片 那就找不到返回none
        #单图的获取方法
        if(singleImgResult):
            imgName = singleImgResult.group(1)
            imgSourceUrl = singleImgResult.group(2)
            print u'这个地址含有1张图片，地址：' +  wholePageUrl 
            print u'正在获取第1张图片.....'
            print u'名字: ' + singleImgResult.group(1)
            print u'源地址：' + singleImgResult.group(2)
            self.getBigImg(imgSourceUrl, wholePageUrl, imgName)
            print 'Done!'
            print '--------------------------------------------------------------------------------------------------------'
        #多图的获取方法
        else:
            wholePageUrl = str(wholePageUrl).replace("medium", "manga")
            pageHtml = self.getPageWithUrl(wholePageUrl)
            totalNumPattern = re.compile('<span class="total">(\d*)</span></div>', re.S)    #找到这一页共有几张图
            totalNum = re.search(totalNumPattern, pageHtml)
            if (totalNum):                      #如果是动图get不到这个num,返回的是none
                print u'这个地址含有' + totalNum.group(1) + u'张图片，地址：' + str(wholePageUrl)
                urlPattern = re.compile('<div class="item-container.*?<img src=".*?".*?data-src="(.*?)".*?</div>', re.S)
                namePattern = re.compile('<section class="thumbnail-container.*?<a href="/member_illust.*?>(.*?)</a>', re.S)
                urlResult = re.findall(urlPattern, pageHtml)
                nameResult = re.search(namePattern, pageHtml)
                for index,item in enumerate(urlResult):
                    print u'正在获取第' + str(index + 1) + u'张图片......'
                    print u'名字: ' + nameResult.group(1) + str(index + 1)
                    print u'源地址：' + item
                    self.getBigImg(item, wholePageUrl, nameResult.group(1)+str(index + 1))                   
                    print 'Done!'
                    print '--------------------------------------------------------------------------------------------------------'
            else:
                print '这个网址是一个gif，跳过!'
                print 'Done!'
                print '--------------------------------------------------------------------------------------------------------'
    
    def start(self):
        self.tag = raw_input('Please input the tag: ')
        self.page = int(raw_input('Please input the page you want to start from: '))
        self.resolution = int(raw_input('Please input the resolution, from 1 to 3, 1 is highest resolution: '))
        path = "/home/zfq/EclipseWork/Pixiv/GetByTag"
        self.mkdir(path, self.tag)  #调用mkdir函数创建文件夹 

        self.getPostKeyAndCookie()   #获得此次会话的post_key和cookie
         
        for pageNum in range(self.page, 100):
            url = "http://www.pixiv.net/search.php?word=%s&s_mode=s_tag_full&order=date_d&type=illust&p=%d"%(self.tag, pageNum)
            pageHtml = self.getPageWithUrl(url)                          #获取该页html
            pageSoup = BeautifulSoup(pageHtml, 'lxml')
            imgItemsResult = pageSoup.find_all("ul", class_="_image-items autopagerize_page_element")  #找到20张图片所在的标签，返回的list长度为1
            imgItemsSoup = BeautifulSoup(str(imgItemsResult), 'lxml')
            imgItemResult = imgItemsSoup.find_all("li", class_="image-item")                       #找到每张图片所在的标签，返回list长度应为20
            imgUrlPattern = re.compile('<a href="(.*?)"><h1.*?</h1>', re.S)                    #在该图片所在image-item标签里找到url和收藏数
            imgStarsPattern = re.compile('<ul class="count-list.*?data-tooltip="(\d*).*?".*?</ul>', re.S)
            for imgItem in imgItemResult:
                if (self.resolution == 1):    #获取原图)
                    imgUrl = re.search(imgUrlPattern, str(imgItem))
                    imgStars = re.search(imgStarsPattern, str(imgItem))
                    if ((not imgStars) or (int(imgStars.group(1)) <= 50)):
                        os.chdir(self.rootPath + '/1-50')      #切换到对应目录
                    elif (int(imgStars.group(1)) <= 300):
                        os.chdir(self.rootPath + '/51-300')
                        self.getImg(imgUrl.group(1))
                    elif(int(imgStars.group(1)) <= 1000):
                        os.chdir(self.rootPath + '/301-1000')
                        self.getImg(imgUrl.group(1))
                    else:
                        os.chdir(self.rootPath + '/1000以上')
                        self.getImg(imgUrl.group(1))

             
p = Pixiv()
p.start()





# 初音ミク

