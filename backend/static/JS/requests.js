const prefix = '/api/v1/';

function makeRequest(url, method="get", data={}){
    console.log(JSON.stringify(data));
    try {
        $.ajax({
            type: method,
            contentType: "application/json",
            dataType: "json",
            url: prefix + url,
            data: JSON.stringify(data),
            success: function (msg) {
                console.log(msg);
                alert("Запрос успешно выполнен: " + msg['message']);
            },
            error: function (msg) {
                console.log(msg);
                let error = 'Неизвестная ошибка :(';
                try {
                    error = msg.responseJSON['message'];
                } catch (e) {}
                alert("Произошла ошибка: " + error);
            }
        });
    } catch (e) {
        console.log(e);
        alert(e);
    }
}

function getChecked(group) {
    let array = [];
    $(group).each(function () {
        if (this.checked) {
            array.push(this.value);
        }
    });
    return array;
}

function urlPart(part) {
    let parts = window.location.pathname.split('/');
    if (parts.length >= part) return parts[part];
    return null;
}

function urlYear() {
    return urlPart(1);
}

function urlSubject() {
    return urlPart(2).split('.')[0];
}

function parseForm(form, data={}) {
    for (const  element of form.getElementsByTagName('input')) {
        if (element.name) {
            let value, field = form[element.name];
            if (element.type === 'checkbox') value = getChecked(field);
            else value = field.value;
            data[element.name] = value;
        }
    }
    for (const element of form.getElementsByTagName('textarea')) {
        data[element.name] = element.value;
    }
    return data;
}

// user

function user_add(form) {
    let login = form['login'].value, password = form['password'].value, password2 = form['password2'].value, status = getChecked(form['status']);
    if (password !== password2) { alert('Пароли не совпадают'); return; }
    if (!login) { alert('Пустой логин'); return; }
    if (!password) { alert('Пустой пароль'); return; }
    makeRequest('user', 'post', {'login': login, 'password': password, 'status': status});
}

function user_delete(form) {
    let id = form['id'].value;
    makeRequest('user/' + id, 'delete');
}

function user_edit_status(form) {
    let data = parseForm(form, {'password': '', 'password_old': '', 'type': 'status'});
    makeRequest('user/' + data['id'], 'put', data);
}

function user_settings(form) {
    let id = form['id'].value, password_old = form['password_old'].value, password = form['password'].value, password2 = form['password2'].value;
    if (!password_old) { alert('Пустой старый пароль'); return; }
    if (password !== password2) { alert('Пароли не совпадают'); return; }
    if (!password) { alert('Пустой пароль'); return; }
    makeRequest('user/' + id, 'put', {'status': [], 'password': password, 'password_old': password_old, 'type': 'password'});
}

// year

function year_add(form) {
    let year = form['year'].value;
    if (Math.abs(year) <= 2000 || Math.abs(year) >= 2100) { alert('Некорректный год'); return; }
    makeRequest('year', 'post', {'year': year});
}

function year_delete(form) {
    let year = form['year'].value;
    makeRequest('year/' + year, 'delete');
}

function year_block(form) {
    let block = form['block'].value, year = urlYear();
    makeRequest('year/' + year, 'put', {'block': block})
}

// subject

function subject_add(form) {
    let data = parseForm(form);
    makeRequest('subject', 'post', data);
}

function subject_edit(form) {
    let data = parseForm(form);
    makeRequest('subject/' + data['id'], 'put', data);
}

function subject_delete(form) {
    let id = form['id'].value;
    makeRequest('subject/' + id, 'delete');
}

// message

function message_add(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('message', 'post', data);
}

function message_edit(form) {
    let data = parseForm(form);
    makeRequest('message/' + data['id'], 'put', data);
}

function message_delete(form) {
    let id = form['id'].value;
    makeRequest('message/' + id, 'delete');
}

// student

function student_registration(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('student', 'post', data);
}

function student_edit(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('student/' + data['id'], 'put', data);
}

function student_delete(form) {
    let id = form['id'].value;
    makeRequest('student/' + id, 'delete');
}

// result

function result_save(form) {
    let data = parseForm(form, {'year': urlYear(), 'subject': urlSubject()});
    makeRequest('result', 'post', data);
}

function result_delete(form) {
    let data = parseForm(form, {'year': urlYear(), 'subject': urlSubject()});
    makeRequest('result', 'delete', data);
}

// group_result

function group_results_save(form) {
    let data = parseForm(form, {'year': urlYear(), 'subject': urlSubject()});
    makeRequest('group_result', 'post', data);
}

// year_subject

function year_subject_save(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('year_subject', 'post', data);
}

function year_subject_edit(form, type) {
    let data = parseForm(form, {'type': type, 'year': urlYear(), 'subject': urlSubject()});
    makeRequest('year_subject/' + data['year'] + '/' + data['subject'], 'put', data);
}

// subject_student

function subject_student_save(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('subject_student', 'post', data);
}

// team

function team_add(form) {
    let data = parseForm(form, {'year': urlYear()});
    makeRequest('team', 'post', data);
}

function team_edit(form) {
    let data = parseForm(form);
    makeRequest('team/' + data['id'], 'put', data);
}

function team_delete(form) {
    let id = form['id'].value;
    makeRequest('team/' + id, 'delete');
}

// team_student

function team_student_add(form) {
    let data = parseForm(form);
    makeRequest('team_student', 'post', data);
}

function team_student_delete(form) {
    let data = parseForm(form);
    makeRequest('team_student', 'delete', data);
}

// student_class

function student_class_delete(form) {
    let id = form['id'].value, year = urlYear();
    makeRequest('student_class/' + year + '/' + id, 'delete');
}
