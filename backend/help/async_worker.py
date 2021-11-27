import threading
import time
from .excel_reader import ExcelReader


class AsyncWorker:
    __worker__ = None
    timer = None
    qtype = 1

    @staticmethod
    def is_alive():
        if AsyncWorker.__worker__:
            if AsyncWorker.__worker__.is_alive():
                return True
            else:
                AsyncWorker.__worker__.join()
                AsyncWorker.__worker__ = None
        return False

    @staticmethod
    def call(filename, year, qtype):
        er = ExcelReader(filename, year, qtype)
        if qtype == 2:
            er.read()
            return
        AsyncWorker.__worker__ = threading.Thread(target=er.read)
        AsyncWorker.__worker__.start()
        AsyncWorker.timer = time.time()

    @staticmethod
    def cur_time():
        if AsyncWorker.timer is None:
            AsyncWorker.timer = time.time()
        return time.time() - AsyncWorker.timer
