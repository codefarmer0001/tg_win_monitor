from db import SQLiteDB
import json

class MonitorKeyWords:
    def __init__(self):
        # 创建或连接到数据库
        self.db = SQLiteDB()
        self.table_name = 'monitor_key_word'
        
        # 检查并应用数据库升级
        # self.db.check_and_apply_upgrade()

        # 创建帐单表
        self.create_table()
        # self.add_column_group_name()

    def create_table(self):
        columns = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- 帐单表的唯一标识符
            user_id TEXT, -- 小飞机id
            account_id INTEGER, -- 用户表id
            keyword TEXT, -- 监听关键词
            send_message TEXT, -- 需要发送的文本
            send_to_group TEXT, -- 需要发送的群组，可以英文逗号分隔
            create_time TIME -- 出/入账时间
        '''
        self.db.create_table(self.table_name, columns)
        # 群组id
        self.db.add_column_if_not_exists(self.table_name, 'group_id', 'INTEGER')


    def insert(self, user_id, account_id, keyword, send_message, send_to_group, create_time):
        data = (None, user_id, account_id, keyword, send_message, send_to_group, create_time, None)
        self.db.insert_data(self.table_name, data)


    def get_all(self):
        return self.db.query_all_data(self.table_name)
    
    def get_data(self, columns, values):
        # 构建查询条件
        conditions = " AND ".join([f"{col} = '{value}'" for col, value in zip(columns, values)])
        print(conditions)
        return self.db.query_all_data(self.table_name, condition = conditions)

    def update_account_type(self, id, type):
        set_values = f"type = '{type}'"
        condition = f"id = {id}"
        self.db.update_data(self.table_name, set_values, condition)


    def update_by_id(self, id, keyword, send_message, send_to_group):
        set_values = f"keyword = '{keyword}', send_message = '{send_message}', send_to_group = '{send_to_group}'"
        condition = f"id = {id}"
        self.db.update_data(self.table_name, set_values, condition)

    def delete_by_id(self, id):
        condition = f"id = {id}"
        self.db.delete_data(self.table_name, condition)

    def get_all_no_group_id(self):
        conditions = 'group_id is null'
        # print(conditions)
        return self.db.query_all_data(self.table_name, condition = conditions)

    def update_group_id(self, group_id, send_to_group):
        set_values = f"group_id = {group_id}"
        condition = f"send_to_group = '{send_to_group}'"
        self.db.update_data(self.table_name, set_values, condition)