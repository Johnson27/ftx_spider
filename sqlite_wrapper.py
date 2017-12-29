import sqlite3
from exception_output import ExceptionOutput
exception = ExceptionOutput()


class SqliteWrapper(object):
    """
    数据库操作封装类,增删改查
    """
    def __init__(self, path):
        self.path = path
        self.conn = self.init_conn()
        self.cursor = self.conn.cursor()

    def init_conn(self):
        """
        获取数据库连接
        """
        try:
            conn = sqlite3.connect(self.path)
            return conn
        except sqlite3.Error as e:
            exception.sqlite_exception(e)

    def create_table(self, command):
        """
        创建表
        """
        if not command:
            exception.sqlite_exception('Empty sql')
            return -1
        try:
            self.cursor.execute(command)
        except sqlite3.Error as e:
            exception.sqlite_exception(e)
            return -2
        return 0

    def insert(self, table, data_dict):
        """
        输入一条记录到数据库
        """
        columns = values = ''
        for key, value in data_dict:
            if(isinstance(value, str)):
                value = ''.join(["'", value, "'"])
            columns += ',' + key
            values += ',' + value
        columns = columns[1:]
        values = values[1:]
        command = 'insert into {table} ({columns}) values ({values})'.format(table=table,columns=columns,values=values)
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            exception.sqlite_exception(e)
            return -1
        except sqlite3.Error as e:
            exception.sqlite_exception(e)
            return -2
        return 0

    def delete(self):
        pass

    def update(self):
        pass

    # select */column1 column2 column3 from table where condition
    def select(self, table, columns='*', condition=''):
        """
        获取数据库记录
        """
        condition = ' where'.join(condition) if condition else ''
        command = 'select {columns} from {table}{condition}'.format(columns=columns, table=table, condition=condition)
        try:
            self.cursor.execute(command)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            exception.sqlite_exception(e)
            return -1

    def close_con(self):
        """
        关闭数据库连接
        """
        self.conn.close()

