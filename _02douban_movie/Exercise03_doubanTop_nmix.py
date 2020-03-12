'''
思路：
1. 访问start_url，获取movie_url信息，再遍历movie_url获取详细信息
2. 构造下一个page_url，获取movie_url信息，遍历访问movie_url获取详细信息
3. 持久化(保存本地，存入mongodb)
'''
import time

import requests
import json
import pymongo
from bson import binary
from gridfs import *
from lxml import etree
from pyquery import PyQuery as pq

class doubanTop_nmix:
    def __init__(self):
        self.start_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        }

    def parse_url(self,url):
        print("visiting {}".format(url))
        response = requests.get(url,headers=self.headers)
        assert response.status_code == 200
        return response

    def get_movie_detail_list(self,response):
        #1. 传入第一页的 url_response ，得到page_movie_url_list
        doc = pq(response.text)
        movie_detail_list = []
        #2. 遍历 page_movie_url_list ,进入到详情页，调用 get_movie_detail 得到 movie_detail
        # fp = self.open_json(path="./config/douban_nmix_conf.json")
        fs = self.get_mongo_collection()
        for item in doc(".hd a").items():
            movie_url = item.attr("href")
            movie_detail_item = self.get_movie_detail(movie_url)
            # self.write_detail_json(fp,movie_detail_item)
            # img_binary = requests.get(url=movie_detail_item['m_img_url'],headers=self.headers,timeout=10).content
            # self.save_detail_to_mongoDB(fs=fs,img_binary=img_binary,item=movie_detail_item)
            self.save_img_bson(item=movie_detail_item)
            movie_detail_list.append(movie_detail_item)
        for i in range(1,10):
            next_page_url = self.start_url + "?start=" + str(i * 25)
            next_page_response = self.parse_url(next_page_url)
            next_url_doc = pq(next_page_response.text)
            for item in next_url_doc(".hd a").items():
                next_movie_url = item.attr("href")
                next_movie_detail_item = self.get_movie_detail(next_movie_url)
                # self.write_detail_json(fp,next_movie_detail_item)
                n_img_binary = requests.get(url=next_movie_detail_item['m_img_url'],headers=self.headers,timeout=10).content
                self.save_detail_to_mongoDB(fs=fs,img_binary=n_img_binary,item=next_movie_detail_item)
                movie_detail_list.append(next_movie_detail_item)
        return movie_detail_list

    def get_movie_detail(self,movie_detail_url):
        response = self.parse_url(movie_detail_url)
        html = etree.HTML(response.text)
        doc = pq(response.text)
        # img_url_list = []
        item = {}
        item['m_rank'] = html.xpath('//span[@class="top250-no"]/text()')[0]
        item['m_name'] = html.xpath('//span[@property="v:itemreviewed"]/text()')[0]
        item['m_img_url'] = html.xpath('//a[@class="nbgnbg"]/img/@src')[0]
        item['m_type'] = html.xpath('//span[@property="v:genre"]/text()')
        item['m_country'] = doc('span:contains("制片国家/地区:")')[0].tail.strip()
        item['m_language'] = doc('span:contains("语言:")')[0].tail.strip()
        item['m_rel_date'] = [item.attr("content") for item in doc('span[property="v:initialReleaseDate"]').items()]
        item['m_run_time'] = doc('span[property="v:runtime"]').text().strip()
        item['m_grade'] = doc('strong[property="v:average"]').text().strip()
        item['m_comments_num'] = html.xpath('//span[@property="v:votes"]/text()')[0]
        item['m_similar_favor_list'] =html.xpath('//div[@class="recommendations-bd"]/dl/dd/a/text()')
        #self.write_detail_json("./config/_02douban_movie.json",item)
        # img_url_list.append(item['m_img_url'])
        return item

    def open_json(self,path):
        fp = open(path,mode="w+",encoding="utf-8")
        return fp

    def write_detail_json(self,fp,item):
        try:
            fp.write(json.dumps(item,ensure_ascii=False,indent=2,separators=(",",":")))
            fp.flush()
        except IOError as e:
            print(e)
            fp.close()
        print("Write item successfully!")

    def get_mongo_collection(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["doubanTop"]
        # movie = db["movie"]
        fs = GridFS(db,collection='movie')
        return fs

    def save_detail_to_mongoDB(self,fs,img_binary,item):
        if not fs.find_one({'img_url':item['m_img_url']}):
            fs.put(img_binary,**item)
            print("Save mongo successfully!")
        else:
            print("Error,failed saved!")

    def save_img_bson(self,item):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['doubanTop']
        img_collection = db['movie_bson']
        img_binary = requests.get(item['m_img_url'],headers=self.headers,timeout=10).content
        if not img_collection.find_one({'img_url':item['m_img_url']}):
            item['img_binary'] = binary.Binary(img_binary)
        img_collection.insert_one(item)
        print('Save successfully!')

    def read_mongo_img(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['doubanTop']
        fs = GridFS(database=db,collection='movie')
        count = 1
        for grid_out in fs.find(no_cursor_timeout=True):
            img = grid_out.read() #获取图片数据
            outf = open(f'./config/00{count}.webp','wb')
            outf.write(img)
            time.sleep(3)
            outf.close()
        client.close()
        print("Ended!")

    def run(self):
        response = self.parse_url(self.start_url)
        movie_detail_list = self.get_movie_detail_list(response)
        # self.read_mongo_img()


if __name__ == "__main__":
    douban = doubanTop_nmix()
    douban.run()

