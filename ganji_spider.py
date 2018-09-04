from sqlalchemy import create_engine  
engine=create_engine('sqlite:///ganji_zufang.sqlite',echo=True)  

from sqlalchemy import Table,Column,Integer,String,ForeignKey  
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()
class ZuFang(Base):
    __tablename__ = "zufang"
    id = Column(Integer, primary_key=True)
    title = Column(String(400))
    rent = Column(String(400))
    info = Column(String(400))
    address = Column(String(400))
    
    @classmethod
    def save(cls, data):
        session.add(data)
        session.commit()
        return data.id
        
Base.metadata.create_all(engine)

import requests
from lxml import etree
import webbrowser

def requests_view(response):
    request_url = response.url
    base_url = '<head><base href="%s">'%(request_url)
    base_url = base_url.encode()
    content = response.content.replace(b"<head>",base_url)
    tem_html = open('tmp.html', 'wb')
    tem_html.write(content)
    tem_html.close()
    webbrowser.open_new_tab("tmp.html")

headers = { 
# 'User-Agent' : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36',
'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
}


def parse_data(response, url):
    # requests_view(response)
    html = etree.HTML(response.content.decode())
    items = html.xpath(".//div[@class='f-main-list']/div/div[contains(@class,'f-list-item')]")
    if len(items) == 0:
        webbrowser.open_new_tab(url)
        print(response.url)
        strs = input("请检查验证问题，输入Enter继续：")
        if strs.upper() == "ENTER":
            print("继续爬取")
            # response 中自带一个URL，是响应的url，不是请求的url
            # 会返回响应的路由，而不是真正访问的地址，所以下边必须传一个URL过去
            parse_data(requests.get(url, headers=headers), url) # python内置的回调函数
            return 0

    for i in items:
        title = i.xpath(".//dd[@class='dd-item title']/a/text()")
        rent = i.xpath(".//dd[@class='dd-item info']/div[@class='price']/span/text()")
        info = i.xpath(".//dd[@class='dd-item size']/span/text()")
        address = i.xpath(".//dd[@class='dd-item address']/span/a/text()")
        print(" ".join(title), " ".join(rent), " ".join(rent), " ".join(address))
        zf = ZuFang()
        zf.title = " ".join(title)
        zf.rent = " ".join(rent)
        zf.info = " ".join(info)
        zf.address = " ".join(address)
        zf.save(zf)
    return i

base_url = "http://bj.ganji.com/fang1/o{}/"
for i in range(1,1000):
    request_url = base_url.format(i)
    response = requests.get(request_url,headers=headers)
    print(request_url, "status_code:", response.status_code)
    try:
        parse_data(response, request_url)
    except:
        # 有的页面为空，但status code依然为200，为了防止程序终止，pass
        pass#记录爬取失败的页面
