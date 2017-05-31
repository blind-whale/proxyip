# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import urllib2
import time
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import types


class TestIpPipeline(object):
    def process_item(self, item, spider):
        useable = 0
        if self.proxy_test(item['ip_port']):
            useable = 1
            print '*****useable type:*****'
            print type(useable)
            item = {
                'ip_port': item['ip_port'],
                'schema': item['schema'],
                'useable': useable,
            }
            print '******item[\'useable\'] type******'
            print type(item['useable'])
            return item

        return None


    def proxy_test(self,ip_port):
        proxy_ip = ip_port
        test_url = 'http://101.200.34.13:8080/validip.html'
        proxy_support = urllib2.ProxyHandler({'http':proxy_ip})
        opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler)
        request = urllib2.Request(test_url)
        request.add_header('Accept-Language', 'zh-cn')
        request.add_header('Content-Type', 'text/html; charset=gb2312')
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)')

        try_count =1
        while try_count<=2:
            try:
                f = opener.open(request, timeout=3.0)
                data = f.read()
                print '*******proxy_test::data*****',data
                if 'f68be168-c7e9-4dc0-9d8b-9f9ff258024a' == data:
                    print '********Valid proxy ip********' + ip_port
                    break;
                else:
                    print '********Invalid proxy ip********' + ip_port
                    return False
            except Exception,e:
                print e
                time.sleep(3)
                try_count += 1

        if try_count > 2:
            return False
        return True


class DbStorePipeline(object):

    @classmethod
    def from_settings(cls,settings):
        dbparam = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparam)
        return cls(dbpool)

    def __init__(self, dbpool):
        self.dbpool = dbpool

    def process_item(self, item, spider):
        if item is None:
            return None
        query = self.dbpool.runInteraction(self.db_insert, item)
        query.addErrback(self.handle_error, item, spider)
        return item

    def db_insert(self,tx,item):
        print '*****db_insert******'
        print item
        print '******item[\'useable\'] type******'
        print type(item['useable'])
        sql = 'INSERT INTO proxyip(ip_port,protocol,useable) VALUES(\'%s\',\'%s\',%d)'
        sql = sql % (item['ip_port'],item['schema'],item['useable'])
        params = ()
        print sql
        tx.execute(sql, params)

    def handle_error(self, failure, item, spider):
        print item
        print failure
