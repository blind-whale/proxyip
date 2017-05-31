#!/usr/bin/python
# -*- coding:utf-8 -*-

import scrapy


class IPSpider(scrapy.spiders.Spider):
    name = 'ipspider'
    start_urls = [
        'http://www.89ip.cn/api/?&tqsl=10000&sxa=&sxb=&tta=&ports=&ktip=&cf=1',
        'http://www.kuaidaili.com/free/',
        'http://www.youdaili.net/Daili/http/',
    ]

    def start_requests(self):
        print '*****start_requests****' + str(len(self.start_urls))
        for index in range(len(self.start_urls)):
            if index ==0:
                print '*****start_urls*****' + self.start_urls[0]
                yield scrapy.Request(self.start_urls[0],callback=self.parse1)
            if index==1:
                yield scrapy.Request(self.start_urls[1],callback=self.parse2)
            if index==2:
                yield scrapy.Request(self.start_urls[2],callback=self.parse3)

    # http://www.89ip.cn/api/
    def parse1(self,response):
        body = response.body
        first = body.index('<BR>')
        end = body.rindex('<BR>')
        print '**** first=%d *** end=%d ***' %(first,end)
        body = body[first:end]
        body = body.replace('\"','')
        ips = body.split('<BR>')
        print '************* '
        print ips
        print ' *************'
        for ip in ips:
            ip = ip.strip()
            yield {
                'ip_port': 'http://' + ip,
                'schema': 'http',
            }

    # http://www.kuaidaili.com/free/
    def parse2(self,response):
        for sel in response.css('div#list tbody tr'):
            strs = sel.css('td::text').extract()
            if strs is not None and len(strs)==7:
                ip = strs[0]
                port = strs[1]
                protocol = strs[3].lower()
                ip_port = protocol + '://' + ip + ':' + port
                if ip_port is not None:
                    yield {
                        'ip_port': ip_port,
                        'schema': protocol,
                    }
        url = response.url
        if IPSpider.start_urls[1] ==url:
            sels = response.css('div#listnav li')
            if len(sels)>=2:
                str = sels[-2].css('a::text').extract_first()
                pagenum = int(str)
                count = 2
                while count <= pagenum:
                    next_page = 'http://www.kuaidaili.com/free/inha/%d/' % (count)
                    count +=1
                    print next_page
                    yield scrapy.Request(next_page,callback=self.parse2)



    def parse3(self, response):
        for url in response.css('div.chunlist li p a::attr(href)').extract():
            if url is not None:
                new_page = response.urljoin(url)
                print '******new_page*******' + new_page
                yield scrapy.Request(new_page, callback=self.parse_ip_list)
        temp = response.css('div.pagelist li')
        if len(temp)>=3:
            next_page = temp[-3].css('a::attr(href)').extract_first()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                print '*******next_page******' + next_page
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_ip_list(self, response):
        url = response.url
        #print '****url****', url
        for s in response.css('div.content p::text').extract():
            ip_port = self.getYoudailiIP(s)
            if ip_port is not None:
                yield ip_port

        temp = response.css('div.pagebreak li a::attr(href)').extract()
        if len(temp)>0:
            next_page = temp[-1]
            if '#' != next_page:
                next_page = response.urljoin(next_page)
                print '******next_page*****',next_page
                yield scrapy.Request(next_page, callback=self.parse)

    # 119.7.72.210:808@HTTP#四川省德阳市 联通
    def getYoudailiIP(self, s):
        ip_port = None
        temp = s.rpartition('#')
        if len(temp) == 3:
            ip_port = temp[0]
            results = ip_port.rpartition('@')
            if len(results)==3:
                return {
                    'ip_port': results[2].lower() + '://' + results[0],
                    'schema': results[2].lower(),
                }
        return None
