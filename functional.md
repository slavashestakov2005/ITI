# Функционал
[На главную](README.md)  
В этом файле описаны все запросы, которые обрабатывает сайт.

## Таблица API (`/api/v1/`)
Если не указывается другого, то приняты следующие обозначения
+ post - добавление объекта;
+ put - редактирование объекта;
+ delete - удаление объекта;
+ сохранение - добавление или редактирование;

| Адрес                               | Сущность                        | post                                  | put                       | delete |
|-------------------------------------|---------------------------------|---------------------------------------|---------------------------|--------|
| barcode/<iti_id>                    | штрих-код - школьник            | admin                                 | -                         | admin  |
| group_result                        | гр. результат                   | предметник                            | -                         | -      |
| iti                                 | таблица ИТИ                     | -                                     | admin - статус блокировки | admin  |
| iti/<item_id>                       | ИТИ                             | admin                                 | admin                     | -      |
| iti_subject                         | ИТИ - предмет                   | admin - несколько за запрос           | -                         | -      |
| iti_subject/<iti_id>/<subject_id>   | таблица ИТИ - предмет           | -                                     | admin или предметник      | -      |
| message                             | таблица новостей                | admin                                 | -                         | -      |
| message/<item_id>                   | новость                         | -                                     | admin                     | admin  |
| result                              | инд. результат                  | предметник добавляет, admin сохраняет | -                         | admin  | 
| school                              | таблица школ                    | admin                                 | -                         | -      |
| school/<item_id>                    | школа                           | -                                     | admin                     | admin  |
| student                             | таблица школьников + их классов | admin                                 | -                         | -      |
| student/<item_id>                   | школьник + класс                | -                                     | admin                     | admin  |
| student_class/<iti_id>/<student_id> | школьник - ИТИ                  | -                                     | -                         | admin  |
| subject                             | таблица предметов               | admin                                 | -                         | -      |
| subject/<item_id>                   | предмет                         | -                                     | admin                     | admin  |
| subject_student                     | школьник - предмет              | admin - несколько за запрос           | -                         | -      |
| team                                | таблица команд                  | admin                                 | -                         | -      |
| team/<item_id>                      | команда                         | -                                     | admin                     | admin  |
| team_student                        | школьник - команда              | admin                                 | admin                     | admin  |
| user                                | таблица пользователей           | admin                                 | -                         | -      |
| user/<item_id>                      | пользователь                    | -                                     | admin или user            | admin  |


## Таблица методов без API
| Путь                                  | Метод     | Файл                 | Описание                                                                       | Необх. роль |
|---------------------------------------|-----------|----------------------|--------------------------------------------------------------------------------|-------------|
| error                                 | GET       | help/errors.py       | Возвращает страницу по коду ошибки                                             | -           |
| login                                 | GET, POST | help/login.py        | Вход (выход) на сайт                                                           | -           |
| eljur_login                           | POST      | help/login.py        | Вход через Eljur                                                               | -           |
| logout                                | GET       | help/login.py        | Выход пользователя                                                             | user        |
| <iti_id>/create_barcodes              | GET       | queries/barcodes.py  | Создание Word со штрих-кодами                                                  | admin       |
| <iti_id>/get_barcodes                 | GET       | queries/barcodes.py  | Возвращает Word со штрих-кодами                                                | admin       |
| <iti_id>/get_excel_with_barcodes      | POST      | queries/barcodes.py  | Генерирует Excel со штрих-кодами из переданного диапазона                      | admin       |
| <iti_id>/create_codes                 | GET       | queries/codes.py     | Делает кодировку школьников на ИТИ в Excel                                     | admin       |
| <iti_id>/get_codes                    | GET       | queries/codes.py     | Возвращает Excel с кодировкой школьников                                       | admin       |
| load_data_from_excel_all              | POST      | queries/excel.py     | Загружает все данные из Excel таблицы                                          | full        |
| load_data_from_excel_students         | POST      | queries/excel.py     | Загружает список школьников из Excel таблицы                                   | admin       |
| download_db                           | GET       | queries/excel.py     | Возвращает Excel со всеми данными из БД                                        | admin       |
| <iti_id>/download_iti                 | GET       | queries/excel.py     | Возвращает Excel со всеми данными одного ИТИ                                   | admin       |
| <iti_id>/download_diploma             | GET       | queries/excel.py     | Возвращает Excel со всеми грамотами одного ИТИ                                 | admin       |
| <iti_id>/<sub_pth>/load_result        | POST      | queries/excel.py     | Загружает результаты по предмету из Excel                                      | Предметник  |
| global_settings                       | POST      | queries/full.py      | Сохраняет глобальные настройки (пароль от почты)                               | full        |
| db                                    | GET       | queries/full.py      | Выполняет переданный текстовый запрос к базе данных                            | full        |
| <iti_id>/year_block                   | GET       | queries/full.py      | Блокирует ИТИ                                                                  | admin       |
| restart                               | GET       | queries/full.py      | Перезагружает сайт на reg.ru                                                   | full        |
| <iti_id>/subjects_for_year.html       | GET       | queries/pages.py     | Возвращает страницу с настройками ИТИ                                          | admin       |
| <iti_id>/messages_for_year.html       | GET       | queries/pages.py     | Возвращает страницу с новостями ИТИ                                            | admin       |
| <iti_id>/student_edit.html            | GET       | queries/pages.py     | Возвращает страницу со списком школьников                                      | admin       |
| <iti_id>/excel.html                   | GET       | queries/pages.py     | Возвращает страницу со списком Excel таблиц                                    | admin       |
| settings.html                         | GET       | queries/pages.py     | Возвращает страницу с настройками пользователя                                 | user        |
| <iti_id>/rating_students_check.html   | GET       | queries/pages.py     | Возвращает страницу для простановки галочек на участие в командах              | admin       |
| school_edit.html                      | GET       | queries/pages.py     | Возвращает страницу с настройками школ                                         | admin       |
| <iti_id>/codes.html                   | GET       | queries/pages.py     | Возвращает страницу с данными о кодировке школьников                           | admin       |
| <iti_id>/barcodes_edit.html           | GET       | queries/pages.py     | Возвращает страницу для редактирования информации штрих-код -- школьник        | admin       |
| <iti_id>/student_info                 | POST      | queries/phone_api.py | Возвращает информацию по ID школьника                                          | scaner      |
| <iti_id>/save_barcodes                | POST      | queries/phone_api.py | Сохраняет таблицу с штрих-кодами                                               | scaner      |
| <iti_id>/<subject_id>/save_results    | GET       | queries/phone_api.py | Сохраняет результаты по предмету                                               | Предметник  |
| <iti_id>/<s_path>/add_result          | GET       | queries/results.py   | Возвращает страницу редактирования результатов по предмету                     | Предметник  |
| <iti_id>/<s_path>/class_split_results | GET       | queries/results.py   | Разделяет индивидуальные результаты по параллелям                              | Предметник  |
| <iti_id>/<s_path>/share_results       | GET       | queries/results.py   | Генерирует таблицу с индивидуальными результатами                              | admin       |
| <iti_id>/ratings_update               | GET       | queries/results.py   | Обновляет рейтинги                                                             | admin       |
| <iti_id>/<s_path>/share_group_results | GET       | queries/results.py   | Генерирует таблицу с групповыми результатами                                   | admin       |
| <iti_id>/share_all_results            | GET       | queries/results.py   | Обновляет таблицы по всем предметам                                            | admin       |
|                                       | GET       | queries/simple.py    | Возвращает стартовую страницу последнего ИТИ                                   |             |
| <iti_id>/                             | GET       | queries/simple.py    | Возвращает стартовую страницу ИТИ                                              |             |
| admin_panel                           | GET       | queries/simple.py    | Рисует админ-панель                                                            | user        |
| <path_to_file>                        | GET       | queries/simple.py    | Возвращает статическую страницу, проверяя статус пользователя и доступ к файлу |             |
| <iti_id>/main.html                    | GET       | queries/simple.py    | Рисует стартовую страницу ИТИ                                                  |             |
| <iti_id>/create_students_lists        | GET       | queries/students.py  | Генерирует списки школьников ИТИ по классам                                    | admin       |
| <iti_id>/public_description           | GET       | queries/subjects.py  | Публикует описание всех предметов одного года                                  | admin       |
| <iti_id>/team_edit                    | GET       | queries/teams.py     | Возвращает страницу редактированием команд                                     | admin       |
| <iti_id>/automatic_division           | GET       | queries/teams.py     | Генерирует автоматическое распределение школьников                             | admin       |
| &nbsp;                                |           |                      |                                                                                |             |
| Форма обратной связи                  | —         | Google Forms         | Форма обратной связи для всех участников и организаторов ИТИ                   |             |
