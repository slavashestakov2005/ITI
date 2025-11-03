Это код сайта для провидения ИТИ в гимназии «Универс».


# Введение
Первая версия сайта ИТИ имела много недочетов, её код можно посмотреть в [соседней ветке](https://github.com/slavashestakov2005/ITI/tree/master). Вторая версия пишется с целью устранить эти недочеты, в планах сначала реализовать весь функционал, а потом переключить версии в проде.


# Структура проекта
* [`backend`](./backend/readme.md) - код для FastApi


# Как начать разработку
Конкретные версии библиотек можно посмотреть в `backend/requirements.txt`. Все команды указаны с префиксом `python -m`, замените на свой способ запустить питон.

## Make
Если установлен `make`, то в `Makefile` есть команды для него, пользоваться ими можно вот так: `make test`.

## Прекоммитные проверки
* Установите библиотеку:
```sh
python -m pip install pre_commit
python -m pre_commit install
```
* При изменений прекоммитных проверок, обновите:
```sh
python -m pre_commit install --hook-type pre-commit
python -m pre_commit autoupdate
```

## Кодстайл
* Установите библиотеки:
```sh
python -m pip install black
python -m pip install flake8
python -m pip install isort
```
* Запустите проверку стиля:
```sh
cd backend
python -m flake8
python -m isort --check-only .
```
* Или автоматически отформатируйте:
```sh
cd backend
python -m black .
python -m isort .
```

## Тесты
* Установите библиотеку:
```sh
python -m pip install pytest
```
* Запустите тесты:
```sh
cd backend
python -m pytest 
```


# Авторы
1. Шестаков Вячеслав slavashestakov2005
