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
    let box = element.srcElement;
    let s = box.id.substr(0, box.id.length - 1), t = box.id.substr(-1);
    let box0 = document.getElementById(s + '0');
    let box1 = document.getElementById(s + '1');
    let box2 = document.getElementById(s + '2');
    if (!box.checked){
        box1.checked = true;
    } else{
        box0.checked = false;
        box1.checked = false;
        box2.checked = false;
        box.checked = true;
    }
}

function find_checkboxes() {
    let elements = document.getElementsByTagName('input');
    for (let pos in elements){
        if (elements[pos].type == 'checkbox') elements[pos].addEventListener('click', change_checkbox);
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
