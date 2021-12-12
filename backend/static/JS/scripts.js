function edit(document){
    document.location.replace(window.location + '/edit');
}

function textInput(document, txt){
    var textarea = document.getElementById(txt);
    textarea.style.height = '1px';
    textarea.style.height = (textarea.scrollHeight + 6) + 'px';
}

function addResult(window) {
    document.location.replace(window.location + '/add_result');
}

function addAppeal(window) {
    document.location.replace(window.location + '/add_appeal');
}

function file_type() {
    if (document.getElementById('is_sol').checked) {
        document.getElementById('form_2').style.display = 'block';
        document.getElementById('form_1').style.display = 'none';
    } else {
        document.getElementById('form_1').style.display = 'block';
        document.getElementById('form_2').style.display = 'none';
    }
}

function file_type2() {
    if (document.getElementById('is_sol2').checked) {
        document.getElementById('form_4').style.display = 'block';
        document.getElementById('form_3').style.display = 'none';
    } else {
        document.getElementById('form_3').style.display = 'block';
        document.getElementById('form_4').style.display = 'none';
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
