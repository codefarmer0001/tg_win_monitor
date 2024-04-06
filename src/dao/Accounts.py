from db import SQLiteDB
import json

class Accounts:
    def __init__(self):
        # 创建或连接到数据库
        self.db = SQLiteDB()
        self.table_name = 'accounts'
        
        # 检查并应用数据库升级
        # self.db.check_and_apply_upgrade()

        # 创建帐单表
        self.create_table()
        # self.add_column_group_name()

    def create_table(self):
        columns = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- 帐单表的唯一标识符
            user_id TEXT UNIQUE, -- 小飞机id
            user_name TEXT, -- 用户名
            user_nickname TEXT, -- 用户昵称
            phone TEXT, -- 用户手机号码
            session_path TEXT, -- session路径
            status INTEGER, -- 账号状态，1正常登陆，0账号被封无法登陆
            type INTEGER, -- 0为消息账号，1为监控账号
            create_time TIME -- 出/入账时间
        '''
        self.db.create_table(self.table_name, columns)


    def insert(self, user_id, user_name, user_nickname, phone, session_path, status, type, create_time):
        data = (None, user_id, user_name, user_nickname, phone, session_path, status, type, create_time)
        self.db.insert_data(self.table_name, data)


    def get_all(self):
        return self.db.query_all_data(self.table_name)
    
    def get_data(self, columns, values):
        # 构建查询条件
        conditions = " AND ".join([f"{col} = '{value}'" for col, value in zip(columns, values)])
        print(conditions)
        return self.db.query_data_json(self.table_name, conditions)

    def update_account_type(self, id, type):
        set_values = f"type = '{type}'"
        condition = f"id = {id}"
        self.db.update_data(self.table_name, set_values, condition)

    def delete_account_by_phoen(self, phone):
        condition = f"phone = '{phone}'"
        self.db.delete_data(self.table_name, condition)