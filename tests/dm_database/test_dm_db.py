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


#!/usr/bin/python
#coding:utf-8
import dmPython
try:
    conn = dmPython.connect(user='SYSDBA', password='Sysdba@123',server='118.193.126.254',  port=5236)
    cursor  = conn.cursor()
    try:
        #查询数据
        cursor.execute ("select * from RAG_FLOW.USER")
        res = cursor.fetchall()
        for tmp in res:
            for c1 in tmp:
                print(c1)

        print('python: select success!')
    except (dmPython.Error, Exception) as err:
        print(err)

    conn.close()
except (dmPython.Error, Exception) as err:
    print(err)
