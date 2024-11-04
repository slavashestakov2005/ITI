Это код сайта для провидения ИТИ в гимназии «Универс».  

## Введение
Данный сайт создан после ИТИ 2020, вызвавших у меня большие вопросы, описанные [в документе](https://docs.google.com/document/d/1-kQDHJF7G2VTbGUDE-pVWSsK-hd90rPEaE97XZG1YqY/edit?usp=sharing).  
Сайт разрабатывается при поддержке организаторов ИТИ 2020 (Савокина Е.В. и Проходский А.Н.), а также
учителя информатики Инженерной школы (Вахитова Е.Ю.).  
С 05.09.2021 дизайн сайта сделан с помощью Bootstrap.  
Более подробная документация:
1. [Excel](docs/Excel.md) -- описание Excel-таблиц;
2. [Функциональность](docs/functional.md) -- описание функционала сайта.
3. [Роли](docs/roles.md) -- описание ролей.


## Ссылки
+ Электронная почта `iti.univers106@gmail.com` (создана 2 августа 2021 года для систематизации информации).
+ [Документ](https://docs.google.com/document/d/1-kQDHJF7G2VTbGUDE-pVWSsK-hd90rPEaE97XZG1YqY/edit?usp=sharing) с предложениями по организации.
+ [Таблица](https://drive.google.com/file/d/1v1KRGQv0LXIG6qS9Tl2b0p9_R18J4shq/view?usp=sharing) с результатами ИТИ 2019 и 2020.
+ [Форма](https://docs.google.com/forms/d/e/1FAIpQLSd7FopqmHoR5Ugcg_-ZAs-guy8NHS5PSvvDsx_rYetaPMKxjw/viewform?usp=sf_link) обратной связи.
+ [Сайт](https://slavashestakov2005.pythonanywhere.com/) ИТИ на `PythonAnywhere`.
+ [Бесплатный чистовик](https://iti106.pythonanywhere.com/) сайта.
+ [Платный чистовик](http://iti.univers.su/) сайта.
+ [Репозиторий](https://github.com/linways/table-to-excel) c JavaScript библиотекой для генерации Excel из HTML-таблицы.
+ [Репозитория](https://github.com/slavashestakov2005/ITI-scaner) с приложением для Android.
+ [Папка](https://drive.google.com/drive/folders/1WF8ALf5ctRKGO5r7q5AP5IopGNHC8Va5?usp=drive_link) с APK файлом приложения для Android.


## Установка и запуск
1. Скачайте `Python` [отсюда](https://www.python.org/downloads/), гарантированно работает под версией `3.11` (возможно под версиями начиная с `3.7`). На платном чистовике используется версия `3.10`.
2. Скачайте код сайт из репозитория (Code > Download ZIP).
3. Распакуйте архив в какую-либо директорию и зайдите в неё из `cmd`.
4. Выполните `pip install -r requirements.txt` для установки необходимых библиотек.
5. Запустите файл `python main.py`.
6. Откройте сервер по адресу [`localhost:8080/`](http://localhost:8080/).
7. Сервер работает только при открытой `cmd`, для его остановки можно в `cmd` ввести `Ctrl+C`.
8. При обновлении кода сервера из репозитория, шаг 4 почти всегда можно пропускать.


## Запуск на сайтах
Для `pythonanywhere.com` нужно создать файл `flask_app.py` вида:
```py
from main import *
```

Для `reg.ru` нужен файл `passenger_wsgi.py` вида:
```py
import sys
import os


INTERP = os.path.expanduser("/var/www/u0000000/data/flaskenv/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())


from main import app as application
```

Единственный найденный надёжный способ запустить бота на `reg.ru` (одновременно с сайтом) - это через `ssh` выполнить:
```bash
nohup ../../flaskenv/bin/python bot_simple.py &
```
