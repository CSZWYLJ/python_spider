import requests
import pymongo
import random
import time
import urllib3
from pyquery import PyQuery as pq
from lxml import etree


class dbBook01:
    def __init__(self, start_url):
        self.start_url = start_url
        self.label = ("文学", "流行", "文化", "生活", "经管", "科技")
        self.header = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
            'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
        ]
        self.headers = {
            'User-Agent': random.choice(self.header),
            # "Connection": "close"
        }

    def parse_url(self, url):
        print("正在访问：", url)
        time.sleep(random.choice([i for i in range(1, 8)]))
        urllib3.disable_warnings()
        response = requests.get(url, headers=self.headers, timeout=30)
        assert response.status_code == 200
        return response.text

    def extract_url(self, addr_url):
        if addr_url is self.start_url:
            html = etree.HTML(self.parse_url(addr_url))
            cate_list = []
            for i in self.label:
                cate_name = html.xpath(
                    f'//a[contains(@name,"{i}") and @class="tag-title-wrapper"]/following-sibling::table//a/text()')
                cate_url = html.xpath(
                    f'//a[contains(@name,"{i}") and @class="tag-title-wrapper"]/following-sibling::table//a/@href')
                cate_hot = html.xpath(
                    f'//a[contains(@name,"{i}") and @class="tag-title-wrapper"]/following-sibling::table//b/text()')
                cate_list.append(list(zip(cate_name, cate_url, cate_hot)))
            dict_item = dict(zip(self.label,
                                 cate_list))  # 6个类别对应的6个list，6个list里面都是三元组，dict_item的例子: {"文学":[('小说',"http:..","3243")(..)..],..)
            return dict_item
        else:
            doc = pq(self.parse_url(addr_url))
            book_url_list = [item.attr('href') for item in doc('div[class="info"] h2 a').items()]
            return book_url_list

    def get_detail_item(self, detail_url):
        item = {}
        doc = pq(self.parse_url(detail_url))
        item['r_name'] = doc('span[property="v:itemreviewed"]').text()
        item['r_author'] = doc('#info span a').text().strip()
        item['r_publish'] = doc('#info span:contains("出版社:")')[0].tail.strip() if doc(
            '#info span:contains("出版社:")').size() != 0 else None
        item['r_year'] = doc('#info span:contains("出版年:")')[0].tail.strip() if doc(
            '#info span:contains("出版年:")').size() != 0 else None
        item['r_page'] = doc('#info span:contains("页数:")')[0].tail.strip() if doc(
            '#info span:contains("页数:")').size() != 0 else None
        item['r_price'] = doc('#info span:contains("定价:")')[0].tail.strip() if doc(
            '#info span:contains("定价:")').size() != 0 else None
        item['r_frame'] = doc('#info span:contains("装帧")')[0].tail.strip() if doc(
            '#info span:contains("装帧:")').size() != 0 else None
        item['r_ISBN'] = doc('#info span:contains("ISBN")')[0].tail.strip()
        item['r_mark'] = doc('strong[class="ll rating_num "]').text()
        item['r_comment'] = doc('span[property="v:votes"]').text()
        if item['r_name'].find(".") != -1:
            item['r_name'] = item['r_name'].replace(".", "-")
        return item

    def get_page_detail_list(self, dict_item):  # 样例：{"文学":[('小说',"http:..","3243")(..)..],..,"经管":[("经济学"..)])
        for k, v in dict_item.items():  # it指向cate列表
            label_item = {}
            label_list = []
            cot = 1
            if k == "科技":
                for x in v:  # 对每一个cate
                    cate_url = "https://book.douban.com" + x[1]  # 得到url
                    book_url_list = self.extract_url(addr_url=cate_url)
                    cate_item = {}
                    book_item_list = []
                    count = 1
                    for book_url in book_url_list:  # 第一页的书籍列表
                        item = {}
                        book_item = self.get_detail_item(book_url)
                        temp = book_item['r_name']
                        book_item.pop('r_name')
                        item[temp] = book_item
                        book_item_list.append(item)
                        count += 1
                        if count == 6:
                            break
                    for page in range(1, 4):  # 70 翻页
                        next_page_url = f"https://book.douban.com/tag/{x[0]}?start={page * 20}&type=T"
                        print(f"正在进行{page + 1}页")
                        next_url_list = self.extract_url(addr_url=next_page_url)
                        count = 1
                        for url in next_url_list:
                            item = {}
                            next_book_item = self.get_detail_item(url)
                            temp = next_book_item['r_name']
                            next_book_item.pop('r_name')
                            item[temp] = next_book_item
                            book_item_list.append(item)
                            count += 1
                            if count == 6:
                                break
                    cate_item[x[0]] = book_item_list
                    label_list.append(cate_item)
                    cot += 1
                    if cot == 3:
                        break
            else:
                continue
            label_item[k] = label_list
            self.save_mongo(label_item)
        return True

    def save_mongo(self, item):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client['dbBook']
        collection = db['another_book']
        if collection.insert_one(item):
            print('Save successfully!')
        else:
            print('Save error')

    def run(self):
        dict_item = self.extract_url(self.start_url)
        label_item = self.get_page_detail_list(dict_item)
        # url = "https://book.douban.com/subject/30307059/"
        # self.get_detail_item(url)


if __name__ == "__main__":
    url = "https://book.douban.com/tag/"
    db = dbBook01(start_url=url)
    db.run()
