# -*- coding: utf-8 -*-

import MySQLdb
import settings
import urllib2

class ProxyHelper:

    def __init__(self):
        self.host = settings.MYSQL_HOST
        self.user =settings.MYSQL_USER
        self.db = settings.MYSQL_DBNAME
        self.passwd = settings.MYSQL_PASSWD
        self.port = 3306

    def connectMySQL(self):
        conn = MySQLdb.connect(
            host=self.host,
            port=self.port,
            db=self.db,
            user=self.user,
            passwd=self.passwd,
            charset='utf8'
        )
        return conn

    def getProxyIp(self):
        ips = self.getRandomIps(10)
        try_count = 0
        while try_count <10:
            for ip in ips:
                if self.test_proxy_ip(ip['ip_port']):
                    return ip
                else:
                    self.db_delete_ip(ip)
            ips = self.getRandomIps(10)
            try_count+=1
        print '*************Proxy IP is not available.*****************'
        return None

    def save_ip(self,item):
        if self.test_proxy_ip(item['ip_port']):
            self.db_insert_ip(item)


    def getRandomIps(self,num):
        sql = 'SELECT * FROM proxyip ORDER BY RAND() LIMIT %d' % (num)
        conn = self.connectMySQL()
        cur = conn.cursor()
        ips = []
        try:
            cur.execute(sql)
            results = cur.fetchall()
            for row in results:
                dict = {}
                dict['id'] = row[0]
                dict['ip_port'] = row[1]
                dict['protocol'] = row[2]
                dict['useable'] = row[3]
                ips.append(dict)
        except Exception,e:
            print e
        cur.close()
        conn.close()
        return ips

    def db_select_all(self):
        conn = self.connectMySQL()
        sql = 'SELECT * FROM proxyip'
        cur = conn.cursor()
        try:
            cur.execute(sql)
            for row in cur.fetchall():
                yield {
                    'id':row[0],
                    'ip_port':row[1],
                    'protocol':row[2],
                    'useable':row[3],
                }
        except Exception,e:
            print e
        cur.close()
        conn.close()

    def db_delete_ip(self,ip):
        sql = 'DELETE FROM proxyip WHERE id=%d' % (ip['id'])
        conn = self.connectMySQL()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            print '************Delete proxy ip:****************' + ip['ip_port']
        except Exception,e:
            print e
            conn.rollback()
        cur.close()
        conn.close()

    def db_insert_ip(self,item):
        sql = 'INSERT INTO proxyip (ip_port,protocol,useable) VALUES (\'%s\',\'%s\',%d)'
        sql = sql % (item['ip_port'],item['schema'],item['useable'])
        conn = self.connectMySQL()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            print '*******save ip successed.*******' + item['ip_port']
        except Exception,e:
            print e
            conn.rollback()
            print '*******save ip failed.*******' + item['ip_port']
        cur.close()
        conn.close()

    def test_proxy_ip(self,ip):
        url = 'http://101.200.34.13:8080/validip.html'
        proxy_support = urllib2.ProxyHandler({'http':ip})
        opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header('Accept-Language','zh-cn')
        #request.add_header('Content-Type','text/html; charset=gb2312')
        request.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)')
        try_count = 0
        while try_count<=2:
            try:
                f = opener.open(request,timeout=5.0)
                data = f.read()
                if 'f68be168-c7e9-4dc0-9d8b-9f9ff258024a' == data:
                    print '************valid proxy ip*****************'
                    break
                else:
                    print '*******invalid proxy ip*******' + ip
                    return False
            except Exception,e:
                print e
                try_count+=1
        if try_count>2:
            return False
        return True