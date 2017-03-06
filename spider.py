from urllib import request as req
from urllib.error import HTTPError, URLError
from lxml import html
from time import sleep
import sys
import os
import io

userAgent = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
imgNum = 0

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
        
def DownloadUrlToFile(url, file):
    try:
        req.urlretrieve(url, file)
    except HTTPError as e:
        fp = open(file, 'w')
        fp.write('download {0} error'.format(url))
        fp.close()
        print('download {0} error : {1}'.format(url, e.reason))
        return e.code
    return 0

def DownloadImg(sex, images, savePath):
    global imgNum
    global userAgent
    savePathName = os.path.join(savePath, sex)
    downloadRet =0
    if not os.path.exists(savePathName):
        os.mkdir(savePathName)
    for img in images:
        downloadRet = DownloadUrlToFile(img.get('data-src'), os.path.join(savePathName, '{0}.{1}.jpg'.format(sex, imgNum)))
        if downloadRet != 404 and downloadRet != 0:
            count = 5
            while count != 0:
                downloadRet = DownloadUrlToFile(img.get('data-src'), os.path.join(savePathName, '{0}.{1}.jpg'.format(sex, imgNum)))
                if downloadRet == 0 or downloadRet == 404:
                    break
                else:
                    count -= 1
        sleep(1)
        imgNum += 1

def AnalysisInfo(tags):
    global imgNum
    infos = {}
    info = []
    for tag in tags:
        if len(tag.getchildren()) < 1:
            continue
        child = tag.getchildren()[0]
        if child.tag == 'img':
            info.append(child.get('data-src'))
        elif child.tag == 'section':
            childInfos = child.getchildren()
            for childInfo in childInfos:
                if len(childInfo.text_content()) > 0:
                    info.append(childInfo.text_content())
                else:
                    if len(childInfo.getchildren()) < 1:
                        continue
                    childSpan = childInfo.getchildren()[0]
                    if childSpan.tag == 'span':
                        info.append(childSpan.text_content())
                    elif childSpan.tag == 'br':
                        infos[imgNum] = info
                        info = []
                        imgNum += 1
                        break
    infos[imgNum] = info
    imgNum += 1
    return infos

def CollectInfo(tags):
    global imgNum
    infos = {}
    info = []
    for tag in tags:
        if len(tag.text_content()) > 0:
            info.append(tag.text_content())
        else:
            child = tag.getchildren()[0]
            if child.tag == 'span' and len(child.text_content()) > 0:
                info.append(child.text_content())
            elif child.tag == 'br':                
                infos[imgNum] = info
                info = []
                imgNum += 1
                continue
    infos[imgNum] = info
    imgNum += 1
    return infos

def ParseHtml(htmlContent, cssSelect):
    tree = html.fromstring(htmlContent)
    content = tree.cssselect(cssSelect)
    return content

def GetHtmlContent(url):
    global userAgent
    try:
        request = req.Request(url, headers = userAgent)
        htmlContent = req.urlopen(request).read().decode('utf-8')
    except URLError as e:
        print('URLError : open {0} error : {0}'.format(url, e.reason))
        return None
    except HTTPError as e:
        print('HTTPError : open {0} error : {1}, status code : {2}'.format(url, e.reason, e.code))
        return None
    return htmlContent

def ParseConfigFile(conf):
    ret = {}
    name = ''
    urls = []
    try:
        fp = open(conf)
    except:
        print('open %s error' % conf)
        return None
    else:
        for line in fp:
            line = line.strip('\r\n')
            if line[0] == '#':
                continue
            if line[0] == '[' and line[-1] == ']':
                if len(name) > 0 and len(urls) > 0:
                    ret[name] = urls
                    name = ''
                    urls = []
                name = line[1:-1]
            if line[:4] == 'http':
                urls.append(line)
        if len(name) > 0 and len(urls) > 0:
            ret[name] = urls
            name = ''
            urls = []
        return ret

# 判断参数
if len(sys.argv) < 3:
    print('Usage:\n%s config_file output_dir' % sys.argv[0])
    sys.exit(-1)


# 判断输出文件夹是否存在
if not os.path.exists(sys.argv[2]):
    os.mkdir(sys.argv[2])

# 解析配置文件
urls = ParseConfigFile(sys.argv[1])

girls = {}
boys = {}

for k, v in urls.items():
    # 编号置零
    imgNum = 0
    # 获取html内容
    for url in v:
        htmlContent = GetHtmlContent(url)
        if (htmlContent == None):
            print('open {0} error.'.format(url))
            continue
        # 获取所有信息承载标签
        tags = ParseHtml(htmlContent, '#js_content section section section')
        # 分析信息
        if k == 'girls':
            girls = AnalysisInfo(tags)
        elif k == 'boys':
            boys = AnalysisInfo(tags)

        print(str(girls))
        print(str(boys))
        # 获取所有img标签
        #images = ParseHtml(htmlContent, '#js_content img')
        # 下载图片
        #DownloadImg(k, images, sys.argv[2])
    
        
    


