Это код сайта для провидения ИТИ в гимназии «Универс».  

## Введение
Данный сайт создан после ИТИ 2020, вызвавших у меня большие вопросы, описанные [в документе](https://docs.google.com/document/d/1-kQDHJF7G2VTbGUDE-pVWSsK-hd90rPEaE97XZG1YqY/edit?usp=sharing).  
Сайт разрабатывается при поддержке организаторов ИТИ 2020 (Савокина Е.В. и Проходский А.Н.), а также
учителя информатики Инженерной школы (Вахитова Е.Ю.).  
С 05.09.2021 дизайн сайта сделан с помощью Bootstrap.

## Поддерживаемый функционал
| Функция | Необходимая роль | Место реализации | Дата |
| ------- | ----- | ----- | ---- |
| Вход (выход) на сайт | — | users.py | 23.04.21 |
| Изменение настроек | Любая | users.py | 23.04.21 |
| Регистрация, редактирование и удаление новых пользователей | admin | users.py | 23.04.21 |
| Просмотр списка пользователей | admin | users.py, auto_generator.py | 19.09.21 |
| Регистрация, редактирование и удаление участников ИТИ | Любая | students.py | 27.04.21 |
| Поиск результатов участника | — | simple.py | 17.10.21 |
| &nbsp; | | | |
| История и отмена операций | admin | results.py | 22.09.21 |
| Загрузка файлов | admin | files_edit.py | 23.04.21 |
| Редактирование годовых файлов | admin | files_edit.py | 25.04.21 |
| Редактирование глобальных файлов | full | files_edit.py | 25.04.21 |
| Изменение глобальных настроек (пароль от почты) | full | full.py | 02.08.21 |
| SQL запросы к базе данных | full | full.py | 25.08.21 |
| Перевод участников в следующий класс | full | students.py | 27.08.21 |
| &nbsp; | | | |
| Загрузка ИТИ из Excel файла | full | full.py, excel_reader.py | 25.11.21 |
| Загрузка списка школьников из Excel файла | full | full.py, excel_reader.py | 27.11.21 |
| Выгрузка ИТИ в Excel файл | admin | full.py, excel_reader.py | 26.09.21 |
| Выгрузка одного предмета в Excel файл | admin | full.py, excel_subject_writer.py | 26.11.21 |
| Выгрузка кодов школьников в Excel файл | admin | students.py, excel_subject_writer.py | 29.11.21 |
| &nbsp; | | | |
| Работа с новыми ИТИ и предметами | full | full.py, auto_generator.py, file_creator.py | 25.04.21 |
| Блокировка и удаление прошедших ИТИ | full | full.py | 17.09.21 |
| Редактирование годового объявления | admin | subjects.py | 25.08.21 |
| Связь ИТИ и предметов, генерация страниц | admin | subjects.py, auto_generator.py, file_creator.py | 25.04.21 |
| Генерация кодов для участников, таблица со всеми кодами | admin | students.py, auto_generator.py | 05.07.21 |
| Добавление, редактирование и удаление команд | admin | teams.py, auto_generator.py  | 02.12.21 |
| Добавление и удаление участников и руководителей команд | admin | teams.py, auto_generator.py | 16.09.21 |
| Отказ / передумывание участника играть в команде | admin | teams.py, auto_generator.py | 04.12.21 |
| Автоматическое расределение на команды | admin | teams.py, auto_generator.py | 02.12.21 |
| Запись участника на групповой тур | Руководитель | teams.py, auto_generator.py | 16.09.21 |
| &nbsp; | | | |
| Классы, время, номер дня и место проведения туров | admin | subjects.py | 29.11.21 |
| Максимальный балл предмета | Предметник | subjects.py | 19.07.21 |
| Сохранение и предпросмотр результатов | Предметник | results.py | 15.09.21 |
| Удаление результатов | admin | results.py | 22.09.21 |
| Добавление и удаление предметных файлов | Предметник | files_edit.py | 25.11.21 |
| Публикация результатов и протокола | admin | results.py, auto_generator.py | 19.08.21 |
| Публикация рейтинга | admin | results.py, auto_generator.py | 16.09.21 |
| &nbsp; | | | |
| Форма подачи апелляций | Любая | results.py | 23.08.21 |
| Форма обратной связи | — | Google Forms | 02.08.21 |

## Ссылки
+ Электронная почта `iti.univers106@gmail.com` (создана 2 августа для систематизации информации).
+ [Документ](https://docs.google.com/document/d/1-kQDHJF7G2VTbGUDE-pVWSsK-hd90rPEaE97XZG1YqY/edit?usp=sharing) с предложениями по организации.
+ [Таблица](https://drive.google.com/file/d/1v1KRGQv0LXIG6qS9Tl2b0p9_R18J4shq/view?usp=sharing) с результатами ИТИ 2019 и 2020.
+ [Форма](https://docs.google.com/forms/d/e/1FAIpQLSd7FopqmHoR5Ugcg_-ZAs-guy8NHS5PSvvDsx_rYetaPMKxjw/viewform?usp=sf_link) обратной связи.
+ [Сайт](https://test-python-slava-shestakov.herokuapp.com/) ИТИ на `Heroku`.
+ [Сайт](https://slavashestakov2005.pythonanywhere.com/) ИТИ на `PythonAnywhere`.
+ [Чистовик](https://iti106.pythonanywhere.com/) сайта.

## Поддержка Excel
### Загрузка ИТИ из таблицы
+ Лист с кодами (содержит `код` в названии)
  + Имя и фамилия участника (столбец с `имя`)
  + Буква и цифра класса (столбец с `класс`)
  + Шифр (столбец с `код`)
  + Буква команды, если есть (столбец с `команда`)
+ Лист с результатами (содержит `ответы` в названии)
  + Название предмета (столбец с `предмет`)
  + Шифр (столбец с `номер`)
  + Первичный балл (столбец с `балл`, но без `чист`)
### Загрузка списка школьников
+ Лист со школьниками (содержит `код` в названии)
  + Имя и фамилия участника (столбец с `имя`)
  + Буква и цифра класса (столбец с `класс`)
+ Можно загружать рещультаты какого-нибудь ИТИ, как список школьников
### Выгрузка предмета
+ По листу на каждый участвовавший класс (`6 класс`, например)
  + `Место`
  + `Фамилия`
  + `Имя`
  + `Класс` (буква и цифра)
  + `Балл` (первичный)
  + `Балл в рейтинг` (чистый)
### Выгрузка кодов школьников
+ Лист с кодами (`Кодировка`)
  + `Фамилия`
  + `Имя`
  + `Класс` (буква и цифра)
  + `Код`
### Выгрузка всего года
+ Коды участников (`Коды`)
  + `Код`
  + `Фамилия`
  + `Имя`
  + `Класс` (буква и цифра)
  + `Команда` (буква, если есть)
+ Список команд (`Команды`)
  + `Вертикаль`
  + `Название`
+ История операций (`История`)
  + `Время` (yyyy-mm-dd hh:mm:ss)
  + `Пользователь`
  + `Тип` (добавление / обновление / удаление)
  + `Описание` (предмет, код, старый и новый результаты)
  + `Отмена` (кем отменено)
+ `Результаты`
  + `Предмет`
  + `Код`
  + `Балл` (по задачам)
  + `Сумма` (первичный балл)
  + `Чист. балл` (балл в рейтинг)
+ `Групповые результаты`
  + `Команда`
  + `Предмет`
  + `Результат`
  + `Участники`
+ `Апелляции`
  + `Предмет`
  + `Код`
  + `Задания`
  + `Описание` (причина апелляции)

## Установка и запуск
1. Скачайте `Python` [отсюда](https://www.python.org/downloads/).
2. Скачайте код сайт из репозитория (Code > Download ZIP).
3. Распакуйте архив в какую-либо дирректорию и зайдите в неё из `cmd`.
4. Выполните `pip install -r requirements.txt` для установки необходимых библиотек.
5. Запустите файл `python main.py`.
6. Откройте сервер по адресу [`localhost:8080/`](http://localhost:8080/).
7. Сервер работает только при открытой `cmd`, для его остановки можно в `cmd` ввести `Ctrl+C`.
8. При обновлении кода сервера из репозитория, шаг 4 почти всегда можно пропускать.
