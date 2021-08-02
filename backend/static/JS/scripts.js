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
