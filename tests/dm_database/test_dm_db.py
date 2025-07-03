#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
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
