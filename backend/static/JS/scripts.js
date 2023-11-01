function go(url){
    document.location.replace(url);
}

function edit(document){
    go(window.location + '/edit');
}

function textInput(document, txt){
    var textarea = document.getElementById(txt);
    textarea.style.height = '1px';
    textarea.style.height = (textarea.scrollHeight + 6) + 'px';
}

function textAreaInput(textarea){
    textarea.style.height = '1px';
    textarea.style.height = (textarea.scrollHeight + 6) + 'px';
}

function initTextArea(){
    let areas = document.getElementsByClassName('js-textarea');
    for (let textarea of areas){
        textarea.oninput = function(){ textAreaInput(textarea); };
        textAreaInput(textarea);
    }
}

function change_checkbox(element) {
    let rating_plus = document.getElementById("rating_students_check_plus");
    let rating_minus = document.getElementById("rating_students_check_minus");
    let count_plus = parseInt(rating_plus.innerHTML), count_minus = parseInt(rating_minus.innerHTML);
    let box = element.srcElement;
    let s = box.id.substr(0, box.id.length - 1), t = box.id.substr(-1);
    let box0 = document.getElementById(s + '0');
    let box1 = document.getElementById(s + '1');
    let box2 = document.getElementById(s + '2');
    if (!box.checked) {         // zero checked values
        if (t === '0') --count_minus;
        if (t === '2') --count_plus;
        box1.checked = true;
    } else {                    // create one checked value
        if (t != '0' && box0.checked) --count_minus;
        if (t != '2' && box2.checked) --count_plus;
        box0.checked = false;
        box1.checked = false;
        box2.checked = false;
        box.checked = true;
        if (t === '0') ++count_minus;
        if (t === '2') ++count_plus;
    }
    rating_plus.innerHTML = count_plus;
    rating_minus.innerHTML = count_minus;
}

function find_checkboxes(class_name) {
    let elements = document.getElementsByTagName('input');
    for (let pos in elements) {
        let elem = elements[pos];
        if (elem.type == 'checkbox' && elem.classList.contains(class_name)) {
            elem.addEventListener('click', change_checkbox);
        }
    }
}

function cursor(){
    document.getElementById("results_for_focus").focus();
}

function convert(str) {
    str = str.replace(/&amp;/g, "&");
    str = str.replace(/&gt;/g, ">");
    str = str.replace(/&lt;/g, "<");
    str = str.replace(/&quot;/g, '"');
    str = str.replace(/&#039;/g, "'");
    return str;
}

function initHTMLContent() {
    let items = document.getElementsByClassName('js-html-content');
    for(let item of items) item.innerHTML = convert(item.innerHTML.toString());
}

function adminPath(year, subject){
    let path = '/admin_panel?';
    if (year) path += 'year=' + year + '&';
    if (subject) path += 'subject=' + subject;
    return path;
}

function adminPanel(){
    let parts = window.location.pathname.split('/');
    let year = null, subject = null;
    console.log(parts);
    if (parts.length > 1) year = parseInt(parts[1]);
    if (parts.length > 2) subject = parseInt(parts[2]);
    if (isNaN(year)) year = subject = null;
    if (isNaN(subject)) subject = null;
    go(adminPath(year, subject));
}

function chooseYear(year){
    let subject = new URL(window.location).searchParams.get('subject');
    go(adminPath(year, subject))
}

function chooseSubject(subject){
    let year = new URL(window.location).searchParams.get('year');
    if (!year) subject = null;
    go(adminPath(year, subject))
}

function tablesAttributes(){
    for (let table of document.getElementsByTagName('table')) {
        table.setAttribute('border', '1');
        table.setAttribute('cellpadding', '10');
    }
}

function getColumn(table, column) {
    var rows = table.getElementsByTagName('tr');
    return [].slice.call(rows).map(function(tr) {
        return tr.getElementsByTagName('td')[column];
    });
}

function setCheckboxesInColumn(table_name, column_index, value) {
    let table = document.getElementById(table_name);
    for (const element of getColumn(table, column_index).slice(1)) {
        element.children[0].checked = value;
    }
}
