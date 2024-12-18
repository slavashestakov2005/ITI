# Excel
[На главную](../README.md)  
Часть Excel файлов генерируется с помощью JavaScript (на HTML-странице рядом с таблицей есть кнопка, скачивающая эту таблицу) -- такие таблицы здесь не описаны, а описаны все остальные.

## Загрузка БД (`ExcelFullReader`)
+ Каждая таблица БД загружается отдельным листом Excel, название листов и столбцов как в БД.
+ `barcode` (штрих-код)
  + `iti_id` (номер ИТИ)
  + `code` (штрих-код)
  + `student_id` (номер школьника)
+ `code` (обычный вариант кодировки школьников)
  + `iti_id` (номер ИТИ)
  + `student_id` (номер школьника)
  + `code` (код школьника)
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
  + `ind_res_per_day` (количество индивидуальных предметов из одного дня в рейтинг)
  + `ind_prize_policy` (обязательно ли есть все 3 призовых места при равных баллах, `0` - нет, `1` - да)
  + `automatic_division` (алгоритм автоматического распределения на команды, `0` - ручное, `1` - по рейтингу внутри параллели, `2` - по рейтингу внутри класса)
  + `auto_teams` (названия команд для автоматического распределения через пробел, например `1 2 3`)
  + `sum_ind_to_team` (суммировать индивидуальные предметы в рейтинг команд, `0` - нет, `1` - да)
  + `sum_gr_to_ind_policy` (суммировать групповые дни в индивидуальный рейтинг, `0` - нет, `1` -  групповой балл в БД = индивидуальные, групповой = индивидуальный * количество участников)
  + `sum_gr_to_super` (суммировать групповые и командные дни в рейтинг суперчемпиона, `0` - нет, `1` - да)
  + `super_open_policy` (для кого открыт рейтинг суперчемпиона, `0` - админы, `1` - учителя, `2` - все)
  + `students_in_team` (школьников с одной параллели в команде)
  + `encoding_type` (тип используемой кодировки, `0` - у каждого школьника один код, `1` - у каждой работы свой штрих-код)
  + `barcodes` (диапазон штрих-кодов для `encoding_type=1`)
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
  + `name_3` (отчество, может быть пустым)
  + `gender` (пол, `ж` или `Ж` - женский, остальное - мужской)
  + `other_id` (ID личного дела, несколько записываются через `|`)
+ `students_classes` (классы школьников в каждые ИТИ)
  + `student_id` (номер школьника)
  + `iti_id` (номер ИТИ)
  + `class_number` (цифра класса)
  + `class_latter` (буква класса, может быть пустым)
  + `school_id` (номер школы)
+ `student_eljur` (id школьников в Eljur)
  + `student_id` (наш ID)
  + `eljur_id` (ID в Eljur)
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
  + `password` (пароль пользователя, в виде хеша)
  + `status` (права доступа)

## Загрузка списка школьников (`ExcelStudentsReader`)
+ `student` (лист со списком школьников)
  + `name_1` (фамилия)
  + `name_2` (имя)
  + `name_3` (отчество)
  + `gender` (пол, `ж` или `Ж` - женский, остальное - мужской)
  + `other_id` (ID личного дела)
  + `class_number` (цифра класса)
  + `class_latter` (буква класса)
  + `school_id` (ID школы)

## Загрузка результатов (`ExcelResultsReader`)
+ `result` (лист с результатами)
  + `student_code` (код работы школьника)
  + `result` (первичный балл)

## Выгрузка БД (`ExcelFullWriter`)
+ Все листы такие же, как и у `ExcelFullReader`.

## Выгрузка ИТИ (`ExcelItiWriter`)
+ Все листы такие же, как и у `ExcelFullReader`.

## Выгрузка списка грамот (`ExcelDiplomaWriter`)
+ Листы `Индивидуальные туры`, `Групповые туры`, `Командный тур`
  + `Класс` (ученик 9И)
  + `ФИО` (Шестаков Вячеслав)
  + `Место` (за 1 место)
  + `Предмет` (в индивидуальном туре | по математике)

## Выгрузка данных через JavaScript
+ Результаты по предметам (на каждом листе своя параллель)
+ Результаты классов (общий рейтинг и по параллелям или можно выбирать произвольное множество)
+ Рейтинг школьников (можно выбирать произвольное множество)
