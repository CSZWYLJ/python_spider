import requests
import json
import random
import time
from pyquery import PyQuery as pq

'''
思路：
1. 找到起始page的url，分析得到起始page上的电影url
2. 观察每页的url的地址变化，找到规律，构造下一页的page，然后分析得到电影url,将所有的page上的url放置于列表中，保存json到本地
3. 获取刚刚的列表url，逐个遍历并分析获取页面的详细信息，保存json到本地
'''

class doubanSpider(object):
    def __init__(self):
        self.start_url = "http://movie.douban.com/top250"
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }
    
    def parse_url(self,url):
        print("正在访问 ",url)
        time.sleep(random.choice([1,2,3,4,5,6,7,8,9,10]))
        response = requests.get(url=url,headers=self.headers)
        assert response.status_code == 200
        return response

    def get_movie_url(self,response):
        movie_url_list = []
        doc = pq(response.text)
        movie_url = doc(".hd a")
        for movie in movie_url:
            movie_url_list.append(movie.attr("href"))
        for i in range(1,10):
            next_url = self.start_url + "?start=" + str(i * 25)
            print("第{}页URL".format(i + 1))
            time.sleep(random.choice([1,2,3,4,5,6,7]))
            next_url_response = self.parse_url(next_url)
            next_url_doc = pq(next_url_response.text)
            next_movie_url = next_url_doc(".hd a")
            for movie in next_movie_url:
                movie_url_list.append(movie.attr("href"))
        self.save_movie_url_as_json(movie_url_list)
        print("保存{}完毕".format("movie_url_list"))
        return movie_url_list

    def save_movie_url_as_json(self,movie_url_list):
        with open("../movie_url_1.json", "a", encoding="utf-8") as f:
            url_item = {}
            for index,url in enumerate(movie_url_list):
                rank = "url_" + str(index) + ":"
                url_item[rank] = url
            url_data = json.dumps(url_item,indent=2,ensure_ascii=False,separators=(",",":"))
            f.write(url_data)

    def read_movie_list(self,path):
        detail_url_list = []
        with open(path,"r",encoding="utf-8") as f:
            dict_data = json.load(f)
            for v in list(dict_data.values()):
                detail_url_list.append(v)
        print(len(detail_url_list))
        return detail_url_list

    def get_content_list(self,movie_url_list):
        movie_detail_list = []
        fpw = self.write_flush("./config/douban_pq.json")
        for url in movie_url_list:
            item = {}
            movie_response = self.parse_url(url)
            movie_doc = pq(movie_response.text)
            item['movie_rank'] = movie_doc("#content").find(".top250-no").text()
            item['movie_name'] = movie_doc("#content").find("span[property='v:itemreviewed']").text()
            item['movie_type'] = movie_doc("#content").find("span[property='v:genre']").text()
            item['movie_country'] = movie_doc("#info").find("span:contains('制片国家/地区:')")[0].tail.strip()
            item['movie_language'] = movie_doc("#info").find("span:contains('语言:')")[0].tail.strip()
            item['movie_release_date'] = [item.attr("content") for item in movie_doc("#info").children("span[property='v:initialReleaseDate']").items()]
            item['movie_run_time'] = movie_doc("#info").find("span[property='v:runtime']").text()
            item['movie_grade'] = movie_doc("strong").text()
            item['movie_comments_number'] = movie_doc("span[property='v:votes']").text()
            item['movie_similar_favor_list'] = [item.text() for item in movie_doc(".recommendations-bd dl dd a").items()] # 同样换成列表
            print(item)
            self.save_each_detail_item(item,fpw)
            movie_detail_list.append(item)
        return movie_detail_list

    def pq_items_iter(self,pq_items):
        iter_res = []
        for item in pq_items:
            iter_res.append(item.text())
        return iter_res

    def write_flush(self,path):
        fp = open(path,"a+",encoding="utf-8")
        return fp

    def save_each_detail_item(self,detail_item,fpw):# 每次写入一个item字典
        try:
            fpw.writelines(json.dumps(detail_item ,ensure_ascii=False,indent=2,separators=(",",":")))
            fpw.flush()
            print("successfully save item!")
        except IndexError as e:
            fpw.close()
            print(e)
        finally:
            fpw.close()

    def save_movie_detail(self,movie_detail_list):
        with open("doubanT250_pq.json","a",encoding="utf-8") as f:
            for content in movie_detail_list:
                f.write(json.dumps(content,ensure_ascii=False,indent=2,separators=(",",":")))
                f.write("\n")

    def read_json(self,path):
        fpr = open(path,"r",encoding="utf-8")
        data = json.load(fpr)
        return data

    def run(self):
        response = self.parse_url(self.start_url)
        movie_url_list = self.get_movie_url(response)
        self.save_movie_url_as_json(movie_url_list)
        movie_detail_list = self.get_content_list(movie_url_list)
        self.save_movie_detail(movie_detail_list)

if __name__ == "__main__":
    # _02douban_movie = doubanSpider()
    # _02douban_movie.run()
    douban = doubanSpider()
    data = douban.read_json("movie_url_1.json")
    movie_url_list = douban.read_movie_list("movie_url_1.json")
    print(movie_url_list)
    movie_detail_list = douban.get_content_list(movie_url_list)