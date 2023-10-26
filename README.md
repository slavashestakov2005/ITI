Это код сайта для провидения ИТИ в гимназии «Универс».  

## Введение
Данный сайт создан после ИТИ 2020, вызвавших у меня большие вопросы, описанные [в документе](https://docs.google.com/document/d/1-kQDHJF7G2VTbGUDE-pVWSsK-hd90rPEaE97XZG1YqY/edit?usp=sharing).  
Сайт разрабатывается при поддержке организаторов ИТИ 2020 (Савокина Е.В. и Проходский А.Н.), а также
учителя информатики Инженерной школы (Вахитова Е.Ю.).  
С 05.09.2021 дизайн сайта сделан с помощью Bootstrap.

## Поддерживаемый функционал (устарело)
| Функция | Необходимая роль | Место реализации | Дата |
| ------- | ----- | ----- | ---- |
| Вход (выход) на сайт | — | users.py | 23.04.21 |
| Изменение настроек | Любая | users.py | 23.04.21 |
| Регистрация, редактирование и удаление новых пользователей | admin | users.py | 23.04.21 |
| Просмотр списка пользователей | admin | users.py, auto_generator.py | 19.09.21 |
| Регистрация, редактирование и удаление участников ИТИ | Любая | students.py | 15.01.22 |
| Поиск результатов участника | — | simple.py | 17.10.21 |
| &nbsp; | | | |
| История и отмена операций | admin | results.py | 22.09.21 |
| Загрузка файлов | admin | files_edit.py | 23.04.21 |
| Редактирование годовых файлов | admin | files_edit.py | 25.04.21 |
| Рейтинг суперчемпионов | admin | rating.html | 15.01.22 |
| Редактирование глобальных файлов | full | files_edit.py | 25.04.21 |
| Изменение глобальных настроек (пароль от почты) | full | full.py | 02.08.21 |
| SQL запросы к базе данных | full | full.py | 25.08.21 |
| Перевод участников в следующий класс | full | students.py | 27.08.21 |
| &nbsp; | | | |
| Загрузка результатов предмета из Excel файла | Предметник | results.py, excel_results_reader.py | 23.12.21 |
| Загрузка ИТИ из Excel файла | full | full.py, excel_reader.py | 25.11.21 |
| Загрузка списка школьников из Excel файла | full | full.py, excel_reader.py | 27.11.21 |
| Выгрузка ИТИ в Excel файл | admin | full.py, excel_writer.py | 26.09.21 |
| Выгрузка одного предмета в Excel файл | admin | full.py, excel_writer.py | 26.11.21 |
| Выгрузка кодов школьников в Excel файл | admin | students.py, excel_writer.py | 29.11.21 |
| Выгрузка результатов классов в Excel файл | admin | auto_generator.py, excel_writer.py | 12.12.21 |
| Выгрузка списка грамот в Excel файл | admin | auto_generator.py, excel_writer.py | 15.01.22 |
| &nbsp; | | | |
| Работа с новыми ИТИ и предметами | full | full.py, auto_generator.py, file_creator.py | 15.01.22 |
| Блокировка и удаление прошедших ИТИ | full | full.py | 17.09.21 |
| Редактирование годового объявления | admin | subjects.py | 25.08.21 |
| Связь ИТИ и предметов, генерация страниц | admin | subjects.py, auto_generator.py, file_creator.py | 25.04.21 |
| Генерация кодов для участников, таблица со всеми кодами | admin | students.py, auto_generator.py | 05.07.21 |
| Добавление, редактирование и удаление команд | admin | teams.py, auto_generator.py  | 02.12.21 |
| Добавление и удаление участников и руководителей команд | admin | teams.py, auto_generator.py | 16.09.21 |
| Отказ / передумывание участника играть в команде | admin | teams.py, auto_generator.py | 04.12.21 |
| Автоматическое расределение на команды | admin | teams.py, auto_generator.py | 02.12.21 |
| Запись участника на групповой тур | Руководитель | teams.py, auto_generator.py | 16.09.21 |
| Запись на индивидуальный и командный туры | Руководитель | teams.py, auto_generator.py | 07.01.22 |
| &nbsp; | | | |
| Классы, время, номер дня и место проведения туров | admin | subjects.py | 29.11.21 |
| Максимальный балл предмета | Предметник | subjects.py | 19.07.21 |
| Сохранение и предпросмотр результатов | Предметник | results.py | 15.09.21 |
| Удаление результатов | admin | results.py | 22.09.21 |
| Добавление и удаление предметных файлов | Предметник | files_edit.py | 25.11.21 |
| Публикация результатов и протокола | admin | results.py, auto_generator.py | 19.08.21 |
| Публикация рейтинга | admin | results.py, auto_generator.py | 16.09.21 |
| Публикация всех результатов одной кнопкой | admin | results.py, auto_generator.py | 09.02.22 |
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
+ [Репозиторий](https://github.com/linways/table-to-excel) c JavaScript библиотекой для генерации Excel из HTML-таблицы.
+ [Репозитория](https://github.com/slavashestakov2005/ITI-scaner) с приложением для Android.
+ [Папка](https://drive.google.com/drive/folders/1WF8ALf5ctRKGO5r7q5AP5IopGNHC8Va5?usp=drive_link) с APK файлом приложения для Android.

## Поддержка Excel
### Загрузка БД (`ExcelFullReader`)
+ Каждая таблица БД загружается отдельным листом Excel, название листов и столбцов как в БД.
+ `barcode` (штрих-код)
  + `iti_id` (номер ИТИ)
  + `code` (штрих-код)
  + `student_id` (номер школьника)
+ `group_results` (результаты команд)
  + `team_id` (номер команды)
  + `subject_id` (номер предмета)
  + `result` (балл в рейтинг)
  + `position` (место в рейтинге)
+ `ind_days_students` (участие школьников в зачёте за индивидуальные дни)
  + `iti_id` (номер ИТИ)
  + `n_d` (номер дня)
  + `student_id` (номер школьника)
+ `iti` (ИТИ)
  + `id` (номер ИТИ)
  + `name_in_list` (название в списке ИТИ, например `ИТИ ОШ-2019`)
  + `name_on_page` (название на страницах, например `ИТИ-2019`)
  + `classes` (отсортированный список классов, например `5 6 7 8 9`)
  + `ind_days` (количество индивидуальных дней)
  + `default_ind_score` (максимальный балл по индивидуальному предмету по умолчанию)
  + `net_score_formula` (вычисление балла в рейтинг по индивидуальному предмету, `0` - серединная формула, `1` - первичный балл)
  + `sum_ind_to_rating` (количество индивидуальных предметов из одного дня в рейтинг)
  + `ind_prize_policy` (обязательно ли есть все 3 призовых места при равных баллах, `0` - нет, `1` - да)
  + `automatic_division` (алгоритм автоматического распределения на команды, `0` - ручное, `1` - по рейтингу внутри параллели, `2` - по рейтингу внутри класса)
  + `auto_teams` (названия команд для автоматического распределения через пробел, например `1 2 3`)
  + `sum_ind_to_team` (суммировать индивидуальные предметы в рейтинг команд, `0` - нет, `1` - да)
  + `sum_gr_to_super` (суммировать групповые и командные дни в рейтинг суперчемпиона, `0` - нет, `1` - да)
  + `students_in_team` (школьников с одной параллели в команде)
  + `description` (описание, только для просмотра администраторами)
  + `block` (блокировка ИТИ, `0` - нет, `1` - да)
+ `iti_subjects` (предметы ИТИ)
  + `id` (номер предмета ИТИ)
  + `iti_id` (номер ИТИ)
  + `subject_id` (номер предмета)
  + `start` (время начала)
  + `end` (время конца)
  + `classes` (классы)
  + `place` (место проведения)
  + `n_d` (номер дня)
+ `iti_subjects_scores` (максимальный балл за предмет ИТИ)
  + `iti_subject_id` (номер предмета ИТИ)
  + `class_n` (номер класса)
  + `max_value` (максимальный балл)
+ `message` (новости)
  + `id` (номер новости)
  + `iti_id` (номер ИТИ)
  + `title` (заголовок)
  + `content` (тело новости)
  + `time` (время публикации)
  + `priority` (приоритет, чем больше, тем новость выше, `0` - по умолчанию)
+ `result` (результаты)
  + `iti_subject_id` (номер предмета ИТИ)
  + `student_code` (код с работы)
  + `student_id` (номер школьника)
  + `result` (первичный балл)
  + `net_score` (балл в рейтинг)
  + `position` (занятое место)
+ `school` (школа)
  + `id` (номер школы)
  + `name` (название, например `МАОУ «КУГ №1 - Универс»`)
  + `short_name` (короткое название, например `Универс`)
+ `student` (школьники)
  + `id` (номер школьника)
  + `name_1` (фамилия)
  + `name_2` (имя)
  + `name_3` (отчество)
  + `gender` (пол, `ж` или `Ж` - женский, остальное - мужской)
  + `other_id` (ID личного дела)
+ `students_classes` (классы школьников в каждые ИТИ)
  + `student_id` (номер школьника)
  + `iti_id` (номер ИТИ)
  + `class_number` (цифра класса)
  + `class_latter` (буква класса)
  + `school_id` (номер школы)
+ `subject` (предмет)
  + `id` (номер предмета)
  + `name` (название)
  + `short_name` (короткое название)
  + `type` (тип, `i` - индивидуальный, `g` - групповой, `a` - командный)
  + `diploma` (текст диплома)
  + `msg` (текст новости)
+ `subjects_students` (участие школьников в не индивидуальных предметах)
  + `iti_subject_id` (номер предмета ИТИ)
  + `student_id` (номер школьника)
+ `team` (команда)
  + `id` (номер команда)
  + `name` (название)
  + `iti_id` (номер ИТИ)
  + `vertical` (вертикаль)
+ `team_consent` (согласие или отказ на участие в команде)
  + `iti_id` (номер ИТИ)
  + `student_id` (номер школьника)
  + `status` (статус, `+1` - согласие, `-1` - отказ, `0` - значение по умолчанию, неизвестно)
+ `teams_students` (участие школьников в командах)
  + `team_id` (номер команды)
  + `student_id` (номер школьника)
+ `user` (пользователи сайта, т.е. учителя)
  + `id` (номер пользователя)
  + `login` (логин пользователя)
  + `password` (пароль пользователя, ввиде хеша)
  + `status` (права доступа)

### Загрузка списка школьников (`ExcelStudentsReader`)
+ `student` (лист со списком школьников)
  + `name_1` (фамилия)
  + `name_2` (имя)
  + `name_3` (отчество)
  + `gender` (пол, `ж` или `Ж` - женский, остальное - мужской)
  + `other_id` (ID личного дела)
  + `class_number` (цифрв класса)
  + `class_latter` (буква класса)
  + `school_id` (ID школы)

### Загрузка результатов (`ExcelResultsReader`)
+ `result` (лист с результатами)
  + `student_code` (код работы школьника)
  + `result` (первичный балл)

### Выгрузка БД (`ExcelFullWriter`)
+ Все листы такие же, как и у `ExcelFullReader`.

### Выгрузка ИТИ (`ExcelItiWriter`)
+ Все листы такие же, как и у `ExcelFullReader`.

### Выгрузка списка грамот (`ExcelDiplomaWriter`)
+ Листы `Индивидуальные туры`, `Групповые туры`, `Командный тур`
  + `Класс` (ученик 9И)
  + `ФИО` (Шестаков Вячеслав)
  + `Место` (за 1 место)
  + `Предмет` (в индивидуальном туре | по математике)

### Выгрузка данных через JavaScript
+ Результаты по предметам (на каждом листе своя параллель)
+ Результаты классов (общий рейтинг и по параллелям или можно выбирать произвольное множество)
+ Рейтинг школьников (можно выбирать произвольное множество)

## Установка и запуск
1. Скачайте `Python` [отсюда](https://www.python.org/downloads/).
2. Скачайте код сайт из репозитория (Code > Download ZIP).
3. Распакуйте архив в какую-либо дирректорию и зайдите в неё из `cmd`.
4. Выполните `pip install -r requirements.txt` для установки необходимых библиотек.
5. Запустите файл `python main.py`.
6. Откройте сервер по адресу [`localhost:8080/`](http://localhost:8080/).
7. Сервер работает только при открытой `cmd`, для его остановки можно в `cmd` ввести `Ctrl+C`.
8. При обновлении кода сервера из репозитория, шаг 4 почти всегда можно пропускать.
