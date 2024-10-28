import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


from flask import Flask
import traceback
import threading as thr
from time import sleep


app = Flask(__name__)


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Сайт ИТИ временно отключён!</h1>"


@app.route("/pandas")
def panda():
    try:
        import pandas as pd
    except BaseException as ex:
        return "<h1 style='color:red'>Erorr: {}</h1><br>{}".format(ex.__repr__(), traceback.format_exc())
    return "<h1 style='color:green'>Ok import Pandas!</h1>"


@app.route("/numpy")
def nump():
    try:
        import numpy as np
    except BaseException as ex:
        return "<h1 style='color:red'>Erorr: {}</h1><br>{}".format(ex.__repr__(), traceback.format_exc())
    return "<h1 style='color:green'>Ok import Numpy!</h1>"


def slow_func():
    sleep(15)


@app.route("/thr_start")
def thr_start():
    try:
        thread = thr.Thread(target=slow_func)
        thread.start()
    except BaseException as ex:
        return "<h1 style='color:red'>Erorr: {}</h1><br>{}".format(ex.__repr__(), traceback.format_exc())
    return "<h1 style='color:green'>Ok thread started!</h1>"


@app.route("/thr_count")
def thr_count():
    try:
        th = thr.active_count()
    except BaseException as ex:
        return "<h1 style='color:red'>Erorr: {}</h1><br>{}".format(ex.__repr__(), traceback.format_exc())
    return "<h1 style='color:green'>Now {} threads are active</h1>".format(th)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
