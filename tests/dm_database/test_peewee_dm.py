# 安装必要库（命令行中执行）
# pip install peewee mysqlclient  # 或者使用 pymysql：pip install peewee pymysql

from peewee import MySQLDatabase, Model, CharField, IntegerField

# 配置数据库连接（根据实际情况修改）
#db = MySQLDatabase(
#    'rag_flow',      # 数据库名
#    user='SYSDBA',     # 用户名
#    password='Sysdba@123', # 密码
#    host='118.193.126.254',     # 数据库地址
#    port=5236,            # 端口
#    charset='utf8mb4'     # 字符编码
#)
#

db = MySQLDatabase(
    'rag_flow_ttttttt',      # 数据库名
    user='root',     # 用户名
    password='infini_rag_flow', # 密码
    host='localhost',     # 数据库地址
    port=5236,            # 端口
    charset='utf8mb4'     # 字符编码
)

# 定义基础模型（绑定数据库）
class BaseModel(Model):
    class Meta:
        database = db

# 定义数据模型示例
class User(BaseModel):
    name = CharField(max_length=50)
    age = IntegerField()
    email = CharField(max_length=100, unique=True)

# 连接数据库并创建表
if __name__ == '__main__':
    try:
        # 连接数据库
        db.connect()
        
        # 创建表（safe=True 表示如果表存在则不重复创建）
        db.create_tables([User], safe=True)
        
        # 示例操作 - 插入数据
        new_user = User.create(name="张三", age=25, email="zhangsan@example.com")
        print(f"插入成功，ID：{new_user.id}")
        
        # 示例操作 - 查询数据
        query = User.select().where(User.age > 20)
        print("年龄大于20的用户：")
        for user in query:
            print(f"{user.id}: {user.name}, {user.age}岁")
            
    except Exception as e:
        print(f"数据库操作异常：{e}")
        import traceback
        traceback.print_exc()
        print("Exception {} ,excetion info is {}".format(e,traceback.format_exc()))
    finally:
        # 关闭数据库连接
        if not db.is_closed():
            db.close()
