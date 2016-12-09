# -*- coding:utf-8 -*-
#created by zfq
#first edited: 2016.12.08
#first commit 2016.12.09

import requests
import re
import os

s = requests.Session()
class Pixiv:
    
    def __init__(self):
        self.baseUrl = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.LoginUrl = "https://accounts.pixiv.net/api/login?lang=zh"
        self.firstPageUrl = 'http://www.pixiv.net/member_illust.php?id=7210261&type=all'
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
        
    #获取此次session的post_key
    def getPostKey(self):
        loginHtml = s.get(self.baseUrl)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, loginHtml.text)
        self.postKey = result.group(1)

    #获取登陆后的页面
    def getPageAfterLogin(self):
        loginData = {"pixiv_id": self.pixiv_id, "password": self.password, 'post_key': self.postKey, 'return_to': self.return_to} 
        s.post(self.LoginUrl, data = loginData, headers = self.loginHeader)
        targetHtml = s.get(self.firstPageUrl)
        return targetHtml.text

    #获取页面
    def getPageWithUrl(self, url):
        return s.get(url).text

    #获取下一页url
    def getNextUrl(self, pageHtml):
        pattern = re.compile('<ul class="page-list.*?<span class="next.*?href="(.*?)" rel="next"', re.S)
        url = re.search(pattern, pageHtml)
        if url:   
            #如果存在，则返回url
            nextUrl = 'http://www.pixiv.net/member_illust.php' + str(url.group(1))
            return nextUrl
        else:
            return None

    #获取每一页每一张图片的详细页面地址
    def getImgDetailPage(self, pageHtml):
        pattern = re.compile('<li class="image-item.*?<a href="(.*?)" class="work  _work.*?</a>', re.S)
        imgPageUrls = re.findall(pattern, pageHtml)
        return imgPageUrls

    #下载指定url的图片
    def getBigImg(self, sourceUrl, wholePageUrl, name):
        header = {
            'Referer': wholePageUrl,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
        }  
        imgExist = os.path.exists('/home/zfq/EclipseWork/Pixiv/GetByFollow/QianYe/' + name + '.jpg')
        if (imgExist):
            print u'该图片已经存在，不用再次保存，跳过！'
        else:
            img = s.get(sourceUrl, headers = header)
            f = open(name + '.jpg', 'wb') #写入多媒体文件要 b 这个参数
            f.write(img.content)  #多媒体文件要是用conctent！
            f.close()

    #打开图片详细页面，获得图片对应的最大分辨率图片
    def getImg(self, pageUrls):
        #查找本页面内最大分辨率的图片的url的正则表达式
        pattern = re.compile('<div class="_illust_modal.*?<img alt="(.*?)".*?data-src="(.*?)".*?</div>', re.S)
        for pageUrl in pageUrls:
            #之前查找得到的只是图片页面的半截url，这里加上前缀使之完整
            wholePageUrl = 'http://www.pixiv.net' + str(pageUrl)
            pageHtml = self.getPageWithUrl(wholePageUrl)
            result = re.search(pattern, pageHtml)     #如果这个页面只有一张图片，那就返回那张图片的url和名字，如果是多张图片 那就找不到返回none
            if(result):
                imgName = result.group(1)
                imgSourceUrl = result.group(2)
                print u'这个地址含有1张图片，地址：' +  wholePageUrl 
                print u'正在获取第1张图片.....'
                print u'名字: ' + result.group(1)
                print u'源地址：' + result.group(2)
                self.getBigImg(imgSourceUrl, wholePageUrl, imgName)
                print 'Done!'
                print '--------------------------------------------------------------------------------------------------------'
            else:       
                self.getMultipleImg(wholePageUrl)    #否则执行多张图片时的特殊处理方法                            
               
    #多张图片的处理方法            
    def getMultipleImg(self, wholePageUrl):
        imgAlmostSourceUrl = str(wholePageUrl).replace("medium", "manga")
        pageHtml = self.getPageWithUrl(imgAlmostSourceUrl)
        totalNumPattern = re.compile('<span class="total">(\d)</span></div>', re.S)    #找到这一页共有几张图
        totalNum = re.search(totalNumPattern, pageHtml)
        #运行了一段时间报错，因为动图这里处理不了，实在没精力了，暂时不抓动图了吧。。。
        if (totalNum):
            print u'这个地址含有' + totalNum.group(1) + u'张图片，转换后的地址：' + str(imgAlmostSourceUrl)
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
            print u'这个网址是一个gif，实在没精力去研究怎么保存动图了。。跳过吧'
            print 'Done!'
            print '--------------------------------------------------------------------------------------------------------'
        
    #输入文件夹名，创建文件夹
    def mkdir(self, path): 
        path = path.strip()
        isExists = os.path.exists(os.path.join("/home/zfq/EclipseWork/Pixiv/GetByFollow", path))
        if not isExists:
            print u'建了一个名字叫做' + path + u'的文件夹！'
            os.makedirs(os.path.join("/home/zfq/EclipseWork/Pixiv/GetByFollow", path))
            return True
        else:
            print u'名字叫做' + path + u'的文件夹已经存在了！'
            return False
    
    def start(self):
        pathName = 'QianYe'
        self.mkdir(pathName)  #调用mkdir函数创建文件夹！这儿path是文件夹名
        os.chdir(pathName)  #切换到目录
        self.getPostKey()   #获得此次会话的post_key
        firstPageHtml = self.getPageAfterLogin() #从第一页url开始
        imgPageUrls = self.getImgDetailPage(firstPageHtml) #获取第一页所有图片url 
        self.getImg(imgPageUrls)                          #获取第一页所有图片url所指向页面的一张或多张图片
        currentPageUrl = self.getNextUrl(firstPageHtml)
        while(currentPageUrl):
            currentPageHtml = self.getPageWithUrl(currentPageUrl)
            imgPageUrls = self.getImgDetailPage(currentPageHtml)
            self.getImg(imgPageUrls)
            currentPageUrl = self.getNextUrl(currentPageHtml)
             
p = Pixiv()
p.start()