import json
import time
import requests
import random
from lxml import etree


class doubanSpider(object):
    def __init__(self):
        self.url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        }
        # self.Cookies = {
        #     'Cookies' : 'll="118408"; bid=MmYp7noApX4; _vwo_uuid_v2=D225463E5744DA577933F888C09E7DE0B|2e653b0bc0199aeb8e7cefca115f48ff; gr_user_id=18239263-864a-4ab0-9ebf-edd97c03ac02; __utmc=30149280; ap_v=0,6.0; __utma=30149280.296732668.1580214346.1582211088.1582246600.3; __utmz=30149280.1582246600.3.3.utmcsr=_02douban_movie.com|utmccn=(referral)|utmcmd=referral|utmcct=/search; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1582248224%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D1A9byzwvFpa_N_2io3Up0k-OLrsojXzbuhXV7IAOk7a%26wd%3D%26eqid%3Dd6a09f8500774756000000035e4ea062%22%5D; _pk_ses.100001.8cb4=*; _pk_id.100001.8cb4=410c8b83a2dc7738.1582211176.2.1582248586.1582213230.; __utmb=30149280.4.10.1582246600',
        # }

    def parse_url(self,url):
        print(url)
        time.sleep(random.choice([1,2,3,4,5,6,7,8,9,10]))
        response = requests.get(url=url,headers=self.headers)
        assert response.status_code == 200
        return response.content.decode()

    def get_movie_url(self,response): # 获取每一页的电影列表的url
        html = etree.HTML(response)
        movie_url_lists = html.xpath('//div[@class="pic"]/a/@href') # 第一页电影的url
        print(len(movie_url_lists)) # 25
        for i in range(1,10):
            next_url = self.url + "?start=" + str(i * 25)  # 构造下一页的url
            print("第%s页URL" % (i + 1))
            next_url_response = self.parse_url(next_url)
            next_html = etree.HTML(next_url_response)
            next_page_movie_url = next_html.xpath('//div[@class="pic"]/a/@href')
            movie_url_lists.extend(next_page_movie_url)
        self.save_movie_url_as_json(movie_url_lists)
        print("打印 {} 完毕".format("movie_url_list"))
        return movie_url_lists

    def save_movie_url_as_json(self,movie_url_lists):
        with open("../movie_url_1.json", "a", encoding="utf-8") as f:
            url_item = {}
            for index,url in enumerate(movie_url_lists,start=1):
                rank = "url_" + str(index) + ": "
                url_item[rank] = url
            url_data = json.dumps(url_item,ensure_ascii=False,indent=2,separators=(",",":")) # separators用于去除,:后面的空格
            f.write(url_data)

    def read_movie_list(self,path):
        detail_url_list = []
        with open(path, "r", encoding="utf-8") as f:
            dict_data = json.load(f)
            for v in list(dict_data.values()):
                detail_url_list.append(v)
        print(detail_url_list)
        return detail_url_list

    def get_content_list(self,detail_url_list): # 获取电影列表中的详情信息
        count = 0
        movie_detail_list = []
        for url in detail_url_list:
            item = {}
            movie_response = self.parse_url(url)
            movie_html = etree.HTML(movie_response)
            print(movie_html)
            item['movie_rank'] = movie_html.xpath('//span[contains(@class,"top250-no")]/text()')[0]
            item['movie_name'] = movie_html.xpath('//span[contains(@property,"v:itemreviewed")]/text()')[0]
            item['movie_type'] = movie_html.xpath('//span[contains(@property,"v:genre")]/text()')
            # item['movie_country'] = movie_html.xpath('//div[@id="info"]').re_first(r'制片.*</span>(.*)<br>\n').strip()
            # item['movie_language'] = movie_html.xpath('//div[@id="info"]').re_first(r'语言:</span>(.*)<br>\n').strip()
            # item['movie_release_date'] = movie_html.xpath('//span[contains(@property,"v:initialReleaseDate")]/text()').extract()
            item['movie_release_date'] = movie_html.xpath('//span[contains(@property,"v:initialReleaseDate")]/text()')
            #item['movie_run_time'] = movie_html.xpath('//span[contains(@property,"v:runtime")]/text()').extract_first()
            item['movie_run_time'] = movie_html.xpath('//span[contains(@property,"v:runtime")]/text()')[0]
            #item['movie_grade'] = movie_html.xpath('//strong[contains(@property,"v:average")]/text()').extract_first()
            item['movie_grade'] = movie_html.xpath('//strong[contains(@property,"v:average")]/text()')[0]
            # item['movie_comments_number'] = movie_html.xpath('//span[@property="v:votes"]/text()').extract_first()
            item['movie_comments_number'] = movie_html.xpath('//span[@property="v:votes"]/text()')[0]
            # item['movie_similar_favor_list'] = movie_html.xpath('//dd/a/text()').extract() # this is a list
            item['movie_similar_favor_list'] = movie_html.xpath('//dd/a/text()') # this is a list
            print(item)
            movie_detail_list.append(item)
        return movie_detail_list

    def save_movie_detail_json(self,movie_detail_list):
        with open("../doubanTop250.json", "a", encoding="utf-8") as f:
            #for content in movie_detail_list:
                f.write(json.dumps(movie_detail_list,ensure_ascii=False,separators=(",",":"),indent=4)) # 思考为什么不能转成dict？
                f.write("\n")
        print("save movie_detail successfully!")
                # count += 1
                # print("Save the top {} successfully!".format(count))

    def run(self):
        url = "https://movie.douban.com/top250"
        response = self.parse_url(url)
        movie_url_lists = self.get_movie_url(response)
        self.save_movie_url_as_json(movie_url_lists)
        movie_detail_list = self.get_content_list(movie_url_lists)

if __name__ == "__main__":
    douban = doubanSpider()
    # url = "https://movie.douban.com/top250"
    # response = _02douban_movie.parse_url(url)
    # movie_url_lists = _02douban_movie.get_movie_url(response)
    # _02douban_movie.save_movie_url_as_json(movie_url_lists)
    detail_url_list = douban.read_movie_list("./movie_url_1.json")
    content = douban.get_content_list(detail_url_list)
    douban.save_movie_detail_json(content)