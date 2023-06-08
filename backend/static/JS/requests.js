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
                alert("Произошла ошибка: " + msg.responseJSON['message']);
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
    let id = form['id'].value, status = getChecked(form['status']);
    makeRequest('user/' + id, 'put', {'status': status, 'password': '', 'password_old': '', 'type': 'status'})
}

function user_settings(form) {
    let id = form['id'].value, password_old = form['password_old'].value, password = form['password'].value, password2 = form['password2'].value;
    if (!password_old) { alert('Пустой старый пароль'); return; }
    if (password !== password2) { alert('Пароли не совпадают'); return; }
    if (!password) { alert('Пустой пароль'); return; }
    makeRequest('user/' + id, 'put', {'status': [], 'password': password, 'password_old': password_old, 'type': 'password'});
}

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
    let block = form['block'].value, year = urlPart(1);
    makeRequest('year/' + year, 'put', {'block': block})
}
