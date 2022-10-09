# 引入requests模块-第三方模块
import requests
# 引入fake_useragent模块-第三方模块
from fake_useragent import UserAgent 
# 引入urllib模块-第三方模块
from urllib import request
# 引入lxml模块-第三方模块
from lxml import etree
# 引入time模块-內建模块
import time 
# 引入random模块-內建模块
import random 
# 引入json模块-內建模块
import json
# 引入csv模块-內建模块
import csv

# 定义爬虫类，获取豆瓣电影 科幻片 排行榜
class DoubanSpider(object):
    # 定义常用变量
    def __init__(self):
        # URL 
        self.url = 'https://movie.douban.com/j/chart/top_list?'
        # 计数器变量
        self.i = 0
        # 电影类型
        self.type = { 
            'type_name': '科幻',
            'type_number': 17
        }

    # 获取随机headers
    def get_headers(self):
        # 实例化ua对象
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        return headers

    # 获取列表页内容
    def get_html(self, params):
        html = requests.get(url=self.url, params=params, headers=self.get_headers()).text
        return html   

    # 解析列表页
    def parse_html(self, html):
        json_html = json.loads(html)
        return json_html

    # 获取详情页内容 
    def get_two_html(self, url):
        req = request.Request(url=url, headers=self.get_headers())
        res = request.urlopen(req)
        html = res.read().decode('utf8', 'ignore')
        return html
        
    # 解析详情页
    def parse_two_html(self, html):
        parse_html = etree.HTML(html)
        # 书写xpath表达式，提取文本最终使用text()
        director_list = parse_html.xpath('//a[@rel="v:directedBy"]/text()')
        star_list = parse_html.xpath('//a[@rel="v:starring"]/text()')
        summary_list = parse_html.xpath('//span[@property="v:summary"]/text()')
        
        director = ', '.join(director_list)
        star = ', '.join(star_list)
        summary = summary_list[0]
        return director, star, summary   
    
    # 保存数据到csv
    def write_html(self, json_html):   
        # 操作文件
        # a+以追加模式打开文件
        # 添加newline参数避免出现空行
        # 设置encoding参数utf-8格式避免出现中文乱码
        with open('films.csv', 'a+', newline='', encoding='utf-8-sig') as csvfile: 
            # 构建字段名称
            fieldnames = ['名称', '评分', '导演', '主演', '简介']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if (self.i == 0):                
                # 写入字段名，当做表头
                writer.writeheader()

            # 提取数据
            item = {}
            # json列表类型： [{电影1},{电影2},{电影3}...]
            for one in json_html:
                # 名称 + 评分
                item['名称'] = one['title'].strip()
                item['评分'] = float(one['score'].strip())

                # 通过详情页获取内容
                two_html = self.get_two_html(one['url'])
                director, star, summary = self.parse_two_html(two_html)
                # 导演 + 主演 + 简介
                item['导演'] = director.strip()
                item['主演'] = star.strip()
                item['简介'] = summary.strip()

                # 打印数据到控制台
                print(item)

                # 写入数据到文件 
                writer.writerow(item)
                self.i += 1      

    # 获取电影总数
    def total_number(self):
        url = 'https://movie.douban.com/j/chart/top_list_count?type={}&interval_id=100%3A90'.format(
            self.type['type_number'])
        headers = self.get_headers()
        html = requests.get(url=url, headers=headers).json()
        total = int(html['total'])
        return total

    # 主程序入口函数
    def main(self):
        # 获取电影总数
        total = self.total_number()        
        for start in range(0, (total+1), 20):
            # 构建查询参数
            params = {
                'type': self.type['type_number'],
                'interval_id': '100:90',
                'action': '',
                'start': str(start),
                'limit': '20'
            }
            # 调用函数，传递params参数
            html = self.get_html(params)
            json_html = self.parse_html(html)
            self.write_html(json_html)
            # 随机休眠1-3秒
            time.sleep(random.randint(1, 3))

        print('{}电影总数量: {}部'.format(self.type['type_name'], self.i))


if __name__ == '__main__':
    spider = DoubanSpider()
    # 调用入口函数
    spider.main()
