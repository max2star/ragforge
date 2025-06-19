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
import pyodbc

try:
    # 连接信息
    server = "118.193.126.254"
    port = "5236"
    username = "SYSDBA"
    password = "Sysdba@123"  # 如果有其他密码请修改

    # 连接字符串
    conn_str = (
        f"DRIVER={{DM ODBC DRIVER}};"
        f"SERVER={server};"
        f"PORT={port};"
        f"UID={username};"
        f"PWD={password}"
    )

    print("尝试连接到达梦数据库...")
    conn = pyodbc.connect(conn_str)
    print("连接成功！")

    # 执行简单查询测试
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM DUAL")
    result = cursor.fetchone()
    print(f"查询结果: {result}")

    cursor.close()
    conn.close()
    print("连接已关闭")

except Exception as e:
    print(f"连接失败: {str(e)}")