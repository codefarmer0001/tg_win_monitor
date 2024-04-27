from db import SQLiteDB
import json
from datetime import datetime

class GroupAdmins:
    def __init__(self):
        # 创建或连接到数据库
        self.db = SQLiteDB()
        self.table_name = 'group_admins'
        
        # 检查并应用数据库升级
        # self.db.check_and_apply_upgrade()

        # 创建帐单表
        self.create_table()
        # self.add_column_type()
        # self.update_proxy_type()

    def create_table(self):
        columns = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- 代理信息表的唯一标识符
            group_id INTEGER, --群组id
            user_id INTEGER, -- 用户id
            create_time TIME -- 查询时间
        '''
        self.db.create_table(self.table_name, columns)
        self.db.create_table_idx(self.table_name, 'idx_group_admin_id', 'user_id, group_id')


    def insert(self, group_id, user_id, create_time=datetime.now()):
        data = (None, group_id, user_id, create_time)
        self.db.insert_data(self.table_name, data)

    def get_all(self):
        return self.db.query_all_data(self.table_name)

    def get_all_by_status(self, columns, values):
        conditions = " AND ".join([f"{col} = '{value}'" for col, value in zip(columns, values)])
        print(conditions)
        return self.db.query_all_data(self.table_name, condition = conditions)
    
    def get_data(self, columns, values):
        # 构建查询条件
        # conditions = " AND ".join([f"{col} = '{value}'" for col, value in zip(columns, values)])
        conditions = []
        for col, value in zip(columns, values):
            if isinstance(value, int):
                conditions.append(f"{col} = {value}")
            else:
                conditions.append(f"{col} = '{value}'")

        conditions_str = " AND ".join(conditions)
        print(conditions)
        return self.db.query_all_data(self.table_name, conditions)


    def delete_by_id(self, id):
        condition = f"id = {id}"
        self.db.delete_data(self.table_name, condition)
