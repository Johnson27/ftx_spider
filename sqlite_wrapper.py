import sqlite3
import threading
from exception_output import ExceptionOutput
exception = ExceptionOutput()
lock = threading.Lock()


class SqliteWrapper(object):
    """
    数据库操作封装类,增删改查
    """
    def __init__(self, path):
        self.path = path

    def get_conn(self):
        """
        获取数据库连接
        """
        try:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            exception.sqlite_exception("get conn error: %s" % e)

    def close_con(self, conn):
        """
        关闭数据库连接
        """
        conn.close()

    def execute_command(self, command):
        """
        执行每一条数据库命令
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        lock.acquire()
        try:
            cursor.execute(command)
            if 'insert' in command:
                conn.commit()
                return 0
            if 'select' in command:
                return cursor.fetchall()
        except sqlite3.Error as e:
            exception.sqlite_exception("execute command error: %s" % e)
            return -1
        finally:
            self.close_con(conn)
            lock.release()

    def create_table(self, command):
        """
        创建表
        """
        if not command:
            exception.sqlite_exception('Empty sql')
            return -1
        self.execute_command(command)
        return 0

    def insert(self, table, data_dict):
        """
        输入一条记录到数据库
        """
        columns = values = ''
        for key, value in data_dict.items():
            if isinstance(value, str):
                value = ''.join(["'", value, "'"])
            columns += ',' + key
            values += ',' + str(value)
        columns = columns[1:]
        values = values[1:]
        command = 'insert into {table} ({columns}) values ({values})'.format(table=table,columns=columns,values=values)
        return self.execute_command(command)

    def delete(self):
        pass

    def update(self):
        pass

    def select(self, table, columns='*', condition=''):
        """
        获取数据库记录
        """
        condition = ' where'.join(condition) if condition else ''
        command = 'select {columns} from {table}{condition}'.format(columns=columns, table=table, condition=condition)
        return self.execute_command(command)


if __name__ == '__main__':
    sw = SqliteWrapper('ftx_xf.db')
    data = {
        'id': 4,
        'name': 'Kobe',
    }
    sw.insert('test', data)
    db_data = sw.select('test', '*')
    print(db_data)
