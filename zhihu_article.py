from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from lxml import etree
import json
import time
import csv
import re
import json
import datetime
import requests
import pandas as pd

# 登陆知乎
def login_cookie():
    s = Service("./chromedriver")
    browser = webdriver.Chrome(service=s)
    browser.set_page_load_timeout(20)
    browser.set_script_timeout(20)
    try:
        browser.get("https://www.zhihu.com")
    except:
        browser.execute_script("window.stop()")
    time.sleep(5)
    input("请扫码登陆！登陆后按enter")
    cookies = browser.get_cookies()
    print("cookies", cookies)
    jsonCookies = json.dumps(cookies)
    with open("cookies_zhihu.txt",'w') as f:
        f.write(jsonCookies)
    time.sleep(5)
    browser.quit()

def crawler(browser,profile):
    html=etree.HTML(browser.page_source)
    div_list=html.xpath('//div[@class="List"]//div[@class="List-item"]')
    for div in div_list:
        dic={}
        data1=json.loads(div.xpath('.//div[@class="ContentItem ArticleItem"]/@data-zop')[0])
        dic['author_profile']=profile
        dic['article_title']=data1['title']
        data2 = json.loads(div.xpath('.//div[@class="ContentItem ArticleItem"]/@data-za-extra-module')[0])
        url_token= data2['card']['content']['token']
        dic['url_token'] = url_token
        dic['upvote_num'] = data2['card']['content']['upvote_num']
        dic['creation_time'] = data2['card']['content']['publish_timestamp']
        dic['article_text'] = get_article(url_token)
        with open("./articles_0-250.csv", "a+", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, dic.keys())
            writer.writerow(dic)
        print("《"+dic['article_title']+"》已抓取！")
    browser.close()

def get_page(profile):
    url = profile +"/posts"
    browser = open_page(url)
    html = etree.HTML(browser.page_source)
    try:
        page_num = int(html.xpath('//div[@class="Pagination"]/button[@type="button"]')[-2].text)
    except:
        page_num = 1
    print(page_num)
    browser.close()
    return page_num


def get_article(url_token):
    headers = {
        "authority": "zhuanlan.zhihu.com",
        'scheme': 'https',
        'Connection': 'close',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    url = 'https://zhuanlan.zhihu.com/p/' + url_token
    page_text = requests.get(url=url, headers=headers).text
    time.sleep(2)
    tree = etree.HTML(page_text)
    article_texts = tree.xpath('//div[@class="RichText ztext Post-RichText css-4em6pe"]//text()')
    article_text = '\n'.join(article_texts)
    return article_text


def open_page(url):
    s = Service("./chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-extensions")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('headless') #后台运行
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36')

    browser = webdriver.Chrome(service=s,
                               options=options)
    browser.delete_all_cookies()  # 清除所有cookies
    browser.set_page_load_timeout(50)
    browser.set_script_timeout(50)
    try:
        browser.get(url)
    except:
        browser.execute_script("window.stop()")
    time.sleep(2)

    html = etree.HTML(browser.page_source)
    try:
        text = html.xpath('//span[@class="ProfileMainPrivacy-mainContentText"]//text()')
        print(text)
        if '该用户设置了隐私保护，' in text:
            f1 = open("cookies_zhihu.txt")
            cookies = f1.read()
            cookies = json.loads(cookies)
            # 添加cookies到未登录的页面
            for co in cookies:
                browser.add_cookie(co)
    except:
        browser.find_element("xpath",
                         "//button[@class='Button Modal-closeButton Button--plain']").click()
    browser.refresh()
    time.sleep(2) # 等它加载一下……
    #拖动滚动条
    if browser.name=="chrome":
        js="var q=document.body.scrollTop=0"
    else:
        js = "var q=document.getElementById('id').scrollTop=0"
    browser.execute_script(js)
    if browser.name=="chrome":
        js = "var q=document.body.scrollTop=10000"
    else:
        js = "var q=document.documentElement.scrollTop=10000"
    browser.execute_script(js)
    return browser

def main(p):
    profile = p
    # login_cookie()
    page_num = get_page(profile)
    for i in range(1, page_num + 1):
        url = profile + "/posts?page=" + str(i)
        browser = open_page(url)
        crawler(browser,profile)
        print("第" + str(i) + "页爬取完成！")

if __name__ == "__main__":
    df = pd.read_csv('./data/profiles_0-250.csv')
    profiles = df['profiles'].tolist()
    header = ['author_profile','article_title', 'url_token', 'upvote_num', 'creation_time', 'article_text']
    with open("./articles_0-250.csv", "w", encoding="utf-8-sig") as f:
        write = csv.writer(f)
        write.writerow(header)
    num = 1
    for p in profiles:
        print("开始爬取第"+str(num)+"个："+p[29:])
        main(p)
        num=num+1






