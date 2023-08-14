navigator.getUserMedia = ( navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia );
var video, webcamStream, canvas, ctx, radioQuery, url;

function getCameraType(){
	return document.querySelector(radioQuery).value;
}

function stopCamera(){
	if (video.srcObject) video.srcObject.getTracks().forEach(track => track.stop());
	video.srcObject = null;
}

function getConstraints(camera){
	return {audio: false, video: {facingMode: camera}};
}

function changeCamera() {
	var camera = getCameraType();
	if (navigator.getUserMedia) {
		stopCamera();
		navigator.getUserMedia(getConstraints(camera),
			function(stream) { video.srcObject = stream; },
			function(err) { alert('!'); alert(err); }
		);
	} else {
		alert("getUserMedia not supported");
	}
}

function init(video_id, canvas_id, group_id, request_url) {
	video = document.getElementById(video_id);
	canvas = document.getElementById(canvas_id);
	ctx = canvas.getContext('2d');
	radioQuery = 'input[name="' + group_id + '"]:checked';
	url = request_url;
	changeCamera();
	table = document.getElementById('barcodes_table');
}

function updateRow(row_id) {
	let data = new FormData(), request = new XMLHttpRequest();
	let row = document.getElementById(row_id);
	let student_id = row.children[1].children[0].value;
	data.append('student_id', student_id);
	request.responseType = 'json';
	request.open('POST', 'student_info');
	request.addEventListener('load', function(e) {
		let jsonn = request.response;
		if (jsonn['status'] === 'OK') {
			let student = jsonn['student'], cls = jsonn['student_class'];
			row.children[3].innerHTML = student['name_1'];
			row.children[4].innerHTML = student['name_2'];
			row.children[5].innerHTML = cls['class_number'] + cls['class_latter'];
		} else {
			alert('Школьник с ID ' + student_id + ' не существует');
		}
	});
	request.send(data);
}

function addRow(table_element, row_data, inputs, row_id) {
	let row = document.createElement('tr');
	row.id = row_id;
	for(let pos = 0; pos < row_data.length; ++pos) {
		let cell = document.createElement('td');
		if (inputs[pos] === 2) {
			let button = document.createElement("input");
			button.type = "button";
			button.value = row_data[pos];
			button.onclick = function() { updateRow(row_id); };
			cell.appendChild(button);
		} else if (inputs[pos] === 1) {
			let input = document.createElement("input");
			input.setAttribute('type', 'text');
			input.value = row_data[pos];
			cell.appendChild(input);
		} else {
			cell.innerHTML = row_data[pos];
		}
		row.appendChild(cell);
	}
	table_element.appendChild(row);
}

function clearTable(table, codes_cnt) {
	table.innerHTML="";
	let head = ['№', 'ID', 'Обновить', 'Фамилия', 'Имя', 'Класс'], inputs = [0, 0, 0, 0, 0, 0];
	for(let i = 1; i <= codes_cnt; ++i) {
		head.push('Штрих-код №' + i);
		inputs.push(0);
	}
	addRow(table, head, inputs, 'barcodes_table_rows_head');
}

let max_codes, line, table;

function snapshot(){
	canvas.width = video.videoWidth;
	canvas.height = video.videoHeight;
	ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
	let blob = canvas.toBlob(function(blob) {
		let data = new FormData(), request = new XMLHttpRequest();
		let file = new File([blob], 'test.png', { type: 'image/png' });
		data.append('file', file);
		request.responseType = 'json';
		request.open('POST', url);
		request.addEventListener('load', function(e) {
		    let jsonn = request.response;
		    max_codes = 0;
		    line = 1;
		    for (let group of jsonn['groups']) {
		    	let barcodes = group[2];
		    	max_codes = Math.max(max_codes, barcodes.length);
			}
			max_codes++;
		    clearTable(table, max_codes);
			for (let group of jsonn['groups']) {
				let people = group[0], cls = group[1], barcodes = group[2], row = [], inputs = [0];
				row.push(line);
				row.push(people['id']);
				row.push('Обновить');
				row.push(people['name_1']);
				row.push(people['name_2']);
				row.push(cls['class_number'] + cls['class_latter']);
				inputs.push(1);
				inputs.push(2);
				inputs.push(0);
				inputs.push(0);
				inputs.push(0);
				for (barcode of barcodes){
					row.push(barcode);
					inputs.push(1);
				}
				for (let i = barcodes.length; i < max_codes; ++i){
					row.push('');
					inputs.push(1);
				}
				addRow(table, row, inputs, 'barcodes_table_rows_' + line);
				line++;
			}
		});
		request.send(data);
	}, 'image/png');
}

function barcodes_table_add_row() {
	let row = [line, '', 'Обновить', '', '', ''], inputs = [0, 1, 2, 0, 0, 0];
	for (let i = 0; i < max_codes; ++i){
		row.push('');
		inputs.push(1);
	}
	addRow(table, row, inputs, 'barcodes_table_rows_' + line);
	line++;
}

function send_barcodes_table() {
	let data = new FormData(), content = [], request = new XMLHttpRequest(), head_row = true;
	for (let line of table.children) {
		if (!head_row) {
			let current_row = [line.children[1].children[0].value];
			for(let i = 6; i < line.children.length; ++i) {
				let barcode = line.children[i].children[0].value;
				current_row.push(barcode);
			}
			content.push(current_row);
		} else head_row = false;
	}
	data.append('data', JSON.stringify(content));
	request.responseType = 'json';
	request.open('POST', 'save_barcodes');
	request.addEventListener('load', function(e) {
		let jsonn = request.response;
		if (jsonn['status'] !== 'OK') {
			alert(jsonn['msg']);
		} else {
			alert('Данные сохранены');
			table.innerHTML = '';
		}
	});
	request.send(data);
}
