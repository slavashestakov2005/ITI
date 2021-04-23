function edit(document){
    document.location.replace(window.location + '/edit');
}

function textInput(document){
    var textarea = document.getElementById("file_text");
    textarea.style.height = '1px';
    textarea.style.height = (textarea.scrollHeight + 6) + 'px';
}
