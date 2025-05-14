#!/usr/bin/python
#coding:utf-8
import dmPython
try:
    conn = dmPython.connect(user='SYSDBA', password='Sysdba@123',server='118.193.126.254',  port=5236)
    cursor  = conn.cursor()
    print('python: conn success!')
    conn.close()
except (dmPython.Error, Exception) as err:
    print(err)
