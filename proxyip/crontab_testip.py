# -*- coding:utf-8 -*-

import proxyhelper

helper = proxyhelper.ProxyHelper()

for item in helper.db_select_all():
    if not helper.test_proxy_ip(item['ip_port']):
        helper.db_delete_ip(item)