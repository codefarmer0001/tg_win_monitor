import sqlite3
import os

class SQLiteDB:
    def __init__(self, db_path='data/telegram.db', create_if_not_exists=True):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

        if create_if_not_exists and not os.path.exists(self.db_path):
            self._create_empty_db()

        self.connect()
        # self.check_and_apply_upgrade()

    def _create_empty_db(self):
        try:
            open(self.db_path, 'w').close()  # 创建一个空的数据库文件
        except IOError as e:
            print(f"Error creating an empty database file: {e}")

    # def check_and_apply_upgrade(self, table_name, column_name, column):
    #     # 示例升级：添加 email 字段
    #     if not self.column_exists('users', 'email'):
    #         self.add_column('users', 'email', 'TEXT')

    def add_column_comment(self, table_name, column_name, comment):
        try:
            # 在SQLite 3.33.0+版本中，使用ALTER TABLE语句添加注释
            self.cursor.execute(f"COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}'")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding comment to column {column_name} in {table_name}: {e}")

    def create_table(self, table_name, columns):
        try:
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")

    def create_table_idx(self, table_name, idx_name, idx_columns):
        try:
            create_table_sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({idx_columns})"
            self.cursor.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")

    def column_exists(self, table_name, column_name):
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in self.cursor.fetchall()]
            return column_name in columns
        except sqlite3.Error as e:
            print(f"Error checking if column exists: {e}")
            return False

    def add_column(self, table_name, column_name, column_type):
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding column to {table_name}: {e}")

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def create_table(self, table_name, columns):
        try:
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")

    def insert_data(self, table_name, data):
        try:
            placeholders = ', '.join(['?' for _ in range(len(data))])
            insert_data_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            self.cursor.execute(insert_data_sql, data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data into {table_name}: {e}")

    def query_data(self, table_name, condition=None):
        try:
            query_data_sql = f"SELECT * FROM {table_name}"
            if condition:
                query_data_sql += f" WHERE {condition}"
            self.cursor.execute(query_data_sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error querying data from {table_name}: {e}")
            return []

    def update_data(self, table_name, set_values, condition):
        try:
            update_data_sql = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
            self.cursor.execute(update_data_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating data in {table_name}: {e}")

    def delete_data(self, table_name, condition):
        try:
            delete_data_sql = f"DELETE FROM {table_name} WHERE {condition}"
            self.cursor.execute(delete_data_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting data from {table_name}: {e}")

    def query_data_count(self, table_name, condition=None):
        try:
            query_data_sql = f"SELECT count(*) FROM {table_name}"
            if condition:
                query_data_sql += f" WHERE {condition}"

            print(query_data_sql)
            # 执行查询
            self.cursor.execute(query_data_sql)
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error querying data from {table_name}: {e}")
            return 0

    def query_top5_data(self, table_name, order_by_column, condition=None):
        try:
            # 构建查询语句，按指定列降序排序，并限制结果为前5条数据
            query_data_sql = f"SELECT * FROM {table_name} "
            if condition:
                query_data_sql += f" WHERE {condition} "
            
             
            query_data_sql += f" ORDER BY {order_by_column} DESC LIMIT 5"
            
            # 执行查询
            self.cursor.execute(query_data_sql)
            
            # 获取结果集中的所有行
            result = self.cursor.fetchall()
            
            return result
        except sqlite3.Error as e:
            print(f"Error querying top 5 data from {table_name}: {e}")
            return []

    def query_aggregation_data(self, table_name, select_colum, group_by_column, condition=None):
        try:
            # 构建查询语句，按指定列降序排序，并限制结果为前5条数据
            query_data_sql = f"SELECT {select_colum} FROM {table_name} "
            if condition:
                query_data_sql += f" WHERE {condition} "
            
             
            query_data_sql += f" group BY {group_by_column}"
            
            # 执行查询
            self.cursor.execute(query_data_sql)
            
            # 获取结果集中的所有行
            result = self.cursor.fetchall()
            
            return result
        except sqlite3.Error as e:
            print(f"Error querying top 5 data from {table_name}: {e}")
            return []

    def query_data_by_page(self, table_name, order_by_column, pageSize, offset, condition=None):
        try:
            # 构建查询语句，按指定列降序排序，并限制结果为前5条数据
            query_data_sql = f"SELECT * FROM {table_name} "
            if condition:
                query_data_sql += f" WHERE {condition} "
            
             
            query_data_sql += f" ORDER BY {order_by_column} DESC LIMIT {pageSize} OFFSET {offset}"
            
            print(query_data_sql)
            # 执行查询
            self.cursor.execute(query_data_sql)
            
            # 获取查询结果的列名
            columns = [column[0] for column in self.cursor.description]

            # 将查询结果转为字典形式
            result = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
            return result
        except sqlite3.Error as e:
            print(f"Error querying data by page from {table_name}: {e}")
            return []


    def query_colum_data(self, table_name, select_colum, order_by_column, condition=None):
        try:
            # 构建查询语句，按指定列降序排序，并限制结果为前5条数据
            query_data_sql = f"SELECT {select_colum} FROM {table_name} "
            if condition:
                query_data_sql += f" WHERE {condition} "
            
             
            query_data_sql += f" ORDER BY {order_by_column} DESC"
            
            print(query_data_sql)
            # 执行查询
            self.cursor.execute(query_data_sql)
            
            # 获取查询结果的列名
            columns = [column[0] for column in self.cursor.description]

            # 将查询结果转为字典形式
            result = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
            return result
        except sqlite3.Error as e:
            print(f"Error querying data by page from {table_name}: {e}")
            return []


    def query_all_data(self, table_name, order_by_column = None, condition=None):
        try:
            # 构建查询语句，按指定列降序排序，并限制结果为前5条数据
            query_data_sql = f"SELECT * FROM {table_name} "
            if condition:
                query_data_sql += f" WHERE {condition} "
            
            if order_by_column:
                query_data_sql += f" ORDER BY {order_by_column} DESC"
            # print(query_data_sql)
            self.cursor.execute(query_data_sql)
            
            # 获取查询结果的列名
            columns = [column[0] for column in self.cursor.description]

            # 将查询结果转为字典形式
            result = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
            return result
        except sqlite3.Error as e:
            print(f"Error querying top 5 data from {table_name}: {e}")
            return []
        
    def query_data_json(self, table_name, condition=None):
        try:
            query_data_sql = f"SELECT * FROM {table_name}"
            if condition:
                query_data_sql += f" WHERE {condition}"
            self.cursor.execute(query_data_sql)
             # 获取查询结果的列名
            columns = [column[0] for column in self.cursor.description]
            row = self.cursor.fetchone()
            # 将查询结果转为字典形式
            result = dict(zip(columns, row)) if row else None
            print(result)
            return result
        except sqlite3.Error as e:
            print(f"Error querying data from {table_name}: {e}")
            return []
        

    def close(self):
        if self.conn:
            self.conn.close()


    def is_column_exists(self, table_name, column_name):
        # 查询表的元数据，获取列名
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in self.cursor.fetchall()]

        # 检查字段是否存在
        return column_name in columns

    def add_column_if_not_exists(self, table_name, column_name, column_type):
        # cursor = self.conn.cursor()

        # 检查字段是否存在
        if not self.is_column_exists(table_name, column_name):
            # 添加新字段的 SQL 语句
            alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"

            # 执行 SQL 语句
            self.cursor.execute(alter_table_sql)

            # 提交更改
            self.conn.commit()

        # 关闭连接
        # cursor.close()

# # 使用示例
# db = SQLiteDB(create_if_not_exists=True)

# # 创建表
# db.create_table('users', 'id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER')

# # 插入数据
# db.insert_data('users', (1, 'John Doe', 30))
# db.insert_data('users', (2, 'Jane Doe', 25))

# # 查询数据
# users = db.query_data('users')
# print('All users:')
# for user in users:
#     print(user)

# # 更新数据
# db.update_data('users', 'age=31', 'name="John Doe"')

# # 删除数据
# db.delete_data('users', 'name="Jane Doe"')

# # 查询更新后的数据
# updated_users = db.query_data('users')
# print('Updated users:')
# for updated_user in updated_users:
#     print(updated_user)

# # 关闭数据库连接
# db.close()
