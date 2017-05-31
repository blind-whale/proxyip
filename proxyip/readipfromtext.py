# -*- coding: utf-8 -*-

import proxyhelper

f = open('ips.txt', 'r')
line = f.readline()
helper = proxyhelper.ProxyHelper()
while line:
    item = {
        'ip_port': 'http://' + line,
        'schema': 'http',
        'useable': 1,
    }
    helper.save_ip(item)
    line = f.readline()
