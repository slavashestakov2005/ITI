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
