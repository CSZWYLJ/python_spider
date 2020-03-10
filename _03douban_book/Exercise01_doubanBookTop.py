'''
1. 确定 start_url ，获取图书标签(例如文学、流行标签)
2. 根据这些标签获取类别名称、数值以及label_url，保存到list
3. 根据类别的category_url，依次访问这些url
4. 访问这些category_url中的列表信息，得到详情页信息
    4.1 记录详情页信息，包括作者 出版社 出版年份 页数 定价 定价 装帧 丛书 ISBN 评分 推荐书籍
'''
import json

import pymongo
from lxml import etree
from pyquery import PyQuery as pq
import requests


class dbBook:
    def __init__(self,start_url):
        self.start_url = start_url
        self.label = ("文学", "流行", "文化", "生活", "经管", "科技")
        self.item_all = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }

    def parse_url(self,url): # 返回text
        print("正在访问：",url)
        response = requests.get(url,headers=self.headers)
        assert response.status_code == 200
        return response.text

    def get_label_info(self,response): # 第一页 获取类别名称、数值和热值
        # label_cate_url_list = []
        html = etree.HTML(response)
        #doc = pq(self.parse_url(first_url))
        label_cate_list = []
        for i in self.label:
            # 获取label列表
            #标签名称
            label_cate_name_list = html.xpath('//a[contains(@name,"{}") and @class="tag-title-wrapper"]/following-sibling::table//a/text()'.format(i))

            # 标签链接
            #写法一
            # label_cate_url_list = ["https://book.douban.com"+url for url in html.xpath('//a[contains(@name,"{}") and @class="tag-title-wrapper"]/following-sibling::table//a/@href'.format(i))]
            #写法二
            #label_cate_url_list = [x for x in map(lambda x:"https://book.douban.com" + x,[url for url in html.xpath('//a[contains(@name,"{}") and @class="tag-title-wrapper"]/following-sibling::table//a/@href'.format(i))])]
            #写法三
            label_cate_url_list = html.xpath('//a[contains(@name,"{}") and @class="tag-title-wrapper"]/following-sibling::table//a/@href'.format(i))

            # 标签热度
            label_cate_hot_list = html.xpath('//a[contains(@name,"{}") and @class="tag-title-wrapper"]/following-sibling::table//b/text()'.format(i))

            label_cate_list.append(list(zip(label_cate_name_list, label_cate_url_list,label_cate_hot_list)))

            # self.save_list(label_list)

            # label_cate_url = []
            # label_cate_name = []
            # label_cate_hot = []
            # for i in label:
            #     for item in doc(f'a[name="{i}"][class="tag-title-wrapper"]').items():
            #         label_cate_name.extend([x.text() for x in item.siblings(".tagCol").find("a").items()])
            #         label_cate_url.extend([x.attr("href") for x in item.siblings(".tagCol").find("a").items()])
            #         label_cate_hot.extend([x.text() for x in item.siblings(".tagCol").find("b").items()])
            # zip(label_cate_url,label_cate_name,label_cate_hot)
        return label_cate_list

    def get_cate_book_list(self,second_url_list): # 第二页 获取页面的url列表,并且翻页
        count = 1
        # li_zip = list(zip(self.label,second_url_list))
        for i in second_url_list: # second_url_list 是三元组
            # i_item ={} #指向的是label，总共6个
            # cate_list = []
            for j in i:
                j_item = {} #指向6个类别中的cate
                item_list = []
                url = "https://book.douban.com" + j[1] #second url
                doc = pq(self.parse_url(url))
                book_url_list = [item.attr('href') for item in doc('div[class="info"] h2 a').items()] # 书籍链接
                for book_url in book_url_list:
                    # 下面的代码尝试变成独立的函数：
                    # 1. 读取到的item中，选取一个元素作为key,剩下的作为值 2，若选取的是两个元素，则作为元组成键，其他为值
                    # 参数:(item,key,*args) 返回：处理完的字典 ①:{key1:{dicts}}  ②{(key1,key2..):{dicts}}
                    item = {}
                    book_item = self.get_detail(book_url)
                    item_key = book_item['r_name']
                    item[item_key] = self.get_pop_dict(book_item,key='r_name')
                    item_list.append(item)
                    count += 1
                    if count == 6:
                        break
                for page in range(1,70):
                    count = 1
                    next_page_url =f"https://book.douban.com/tag/%E7%90%86%E8%B4%A2?start={page*20}&type=T"
                    print(f'正在进行第{page+1}页')
                    next_doc = pq(self.parse_url(next_page_url))
                    if next_doc('#subject_list .pl2').text() != "没有找到符合条件的图书":
                        next_url_list = [item.attr('href') for item in next_doc('div[class="info"] h2 a').items()]
                        for book_url in next_url_list:
                            item = {}
                            next_book_item = self.get_detail(book_url)
                            temp = next_book_item['r_name']
                            item[temp] = self.get_pop_dict(next_book_item,key='r_name')
                            item_list.append(item)
                            count += 1
                            if count == 4:
                                break
                    if count:
                        break
                    else:
                        break
                j_item[j[0]] = item_list
                self.save_mongo(j_item)
        # for x in li_zip:
        #     i_item[x[0]] = cate_list
                return j_item

    def get_pop_dict(self,dic,key):
        if key in dic:
            dic.pop(key)
        else:
            return None
        return dic

    def get_detail(self,detail_url): # 第三页 详情页 ，或许书籍的各种信息
        item = {}
        doc = pq(self.parse_url(detail_url))
        item['r_name'] = doc('span[property="v:itemreviewed"]').text()
        item['r_author'] = doc('#info span a').text().strip()
        item['r_publish'] = doc('#info span:contains("出版社:")')[0].tail.strip()
        item['r_year'] = doc('#info span:contains("出版年:")')[0].tail.strip()
        item['r_page'] = doc('#info span:contains("页数:")')[0].tail.strip()
        item['r_price'] = doc('#info span:contains("定价:")')[0].tail.strip()
        item['r_frame'] = doc('#info span:contains("装帧:")')[0].tail.strip()
        item['r_ISBN'] = doc('#info span:contains("ISBN:")')[0].tail.strip()
        item['r_mark'] = doc('strong[class="ll rating_num "]').text()
        item['r_comment'] = doc('span[property="v:votes"]').text()
        return item

    def save_list(self, rlist):
        with open("../config/dbBook.json", mode="a", encoding="utf-8") as f:
            f.write(json.dumps(rlist,ensure_ascii=False,indent=4,separators=(",",":")))
            f.write('\n')
            print("Save successfully!")

    def save_mongo(self, item):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client['dbBook']
        collection = db['lable_book']
        if collection.insert_one(item):
            print("Save successfully!")
        else:
            print("Save error!")

    def run(self):
        response = self.parse_url(self.start_url)
        r_item = {}
        label_cate_list = self.get_label_info(response) #得到的是第二页的三元组,6长度
        item = self.get_cate_book_list(label_cate_list)

if __name__ == "__main__":
    url = 'https://book.douban.com/tag/'
    book = dbBook(start_url=url)
    book.run()

