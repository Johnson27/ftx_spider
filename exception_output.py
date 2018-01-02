import threading


lock = threading.Lock()


def locker(func):
    """
    锁decorator
    """
    def wrapper(*args, **kw):
        lock.acquire()
        func(*args, **kw)
        lock.release()

    return wrapper


class ExceptionOutput:
    def __init__(self):
        pass

    @locker
    def spider_exception(self, url, error):
        """
        记录爬取过程中出错的url及错误
        :param url:
        :param error:
        :return:
        """
        with open('spider_exception.txt', 'a') as f:
            line = '{0}: \n{1}\n'.format(url, error)
            f.write(line)
            f.close()

    @locker
    def sqlite_exception(self, error):
        """
        记录数据库出错
        :param error:
        :return:
        """
        with open('sqlite_exception.txt', 'a') as f:
            line = '%s\n' % error
            f.write(line)
            f.close()

    @locker
    def exception_log_clear(self, filename):
        """
        清除错误日志
        :param filename:
        :return:
        """
        with open(filename, 'w') as f:
            f.truncate()
            f.close()
