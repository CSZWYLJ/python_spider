import json
import time
from selenium import webdriver


class HuyaSpider:
    def __init__(self):
        self.start_url = "https://www.huya.com/l"
        self.driver = webdriver.Chrome()

    def get_content_list(self):
        li_list = self.driver.find_elements_by_xpath('//ul[@id="js-live-list"]/li')
        content_list = []
        for li in li_list:
            item = {}
            item['room_name'] = li.find_element_by_xpath('.//span/i').get_attribute("title") # 主播名字
            item['hoster_num'] = li.find_element_by_xpath('.//i[2]').text # 主播热度
            item['hoster_img'] = li.find_element_by_xpath('.//span[@class="txt"]//img').get_attribute('src') # 主播照片
            item['hoster_category'] = li.find_element_by_xpath('.//span/a').text # 主播分类
            item['hoster_title'] = li.find_element_by_xpath('./a[@class="title new-clickstat j_live-card"]').get_attribute('title') # 房间标题
            time.sleep(0.5)
            print(item)
            content_list.append(item)
        next_url = self.driver.find_element_by_xpath('//a[@class="laypage_next"]').text
        next_url = next_url if len(next_url) > 0 else None
        print(next_url)
        print("****"*10)
        return content_list,next_url

    def save_content_list(self,content_list):
        with open("_01huya.json","w",encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content,ensure_ascii=False,indent=2))
                f.write("\n")
        print("Save successfully!")

    def run(self):
        self.driver.get(self.start_url)
        content_list,next_url = self.get_content_list()
        while next_url is not None:
            next_url.click()
            time.sleep(10)
            content_list.next_url = self.get_content_list()
            self.save_content_list()


if  __name__ == "__main__":
    huya = HuyaSpider()
    huya.run()


