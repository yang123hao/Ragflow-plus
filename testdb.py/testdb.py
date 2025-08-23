import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import mysql.connector
from management.server.database import DB_CONFIG

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    print("数据库连接成功!")
    print("连接信息:", connection)
    
    # 测试查询
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM user LIMIT 5")
    results = cursor.fetchall()
    print("前5条记录:")
    for row in results:
         print(row)
    
    cursor.close()
    connection.close()
    print("连接已关闭")
    
except Exception as e:
    print("数据库连接失败:", str(e))
    print("错误类型:", type(e).__name__)