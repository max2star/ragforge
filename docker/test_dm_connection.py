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