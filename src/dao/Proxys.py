from db import SQLiteDB
import json
from datetime import datetime

class Proxys:
    def __init__(self):
        # 创建或连接到数据库
        self.db = SQLiteDB()
        self.table_name = 'proxys'
        
        # 检查并应用数据库升级
        # self.db.check_and_apply_upgrade()

        # 创建帐单表
        self.create_table()
        # self.add_column_group_name()

    def create_table(self):
        columns = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- 代理信息表的唯一标识符
            hostname TEXT UNIQUE, -- 代理ip
            port INTEGER, -- 代理端口号
            user_name TEXT, -- 代理用户名
            password TEXT, -- 代理用户名
            create_time TIME -- 出/入账时间
        '''
        self.db.create_table(self.table_name, columns)
        self.db.create_table_idx(self.table_name, 'idx_hostname_port_secret', 'hostname, port, user_name, password')


    def insert(self, hostname, port, user_name, password, create_time=datetime.now()):
        data = (None, hostname, port, user_name, password, create_time)
        self.db.insert_data(self.table_name, data)


    def get_all(self):
        return self.db.query_all_data(self.table_name)
    
    def get_data(self, columns, values):
        # 构建查询条件
        conditions = " AND ".join([f"{col} = '{value}'" for col, value in zip(columns, values)])
        print(conditions)
        return self.db.query_data_json(self.table_name, conditions)
