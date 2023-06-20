function colorizePlaces() {
    let tables = document.getElementsByClassName('js-table-color-place');
    for(let table of tables) {
        for(let row of table.rows) {
            let cell = row.cells[0].innerText;
            switch (cell) {
                case '1': row.classList.add('p1'); break;
                case '2': row.classList.add('p2'); break;
                case '3': row.classList.add('p3'); break;
            }
        }
    }
}

function orderNumber(a, b) {
    return b - a;
}

function colorizePlacesCols(cols) {
    let tables = document.getElementsByClassName('js-table-color-place');
    for(let cur_table of tables) {
        let table = cur_table.getElementsByTagName('tbody')[0];
        for(let col of cols) {
            let res = new Set();
            for(let row of table.rows) {
                let cell = row.cells[col].innerText;
                res.add(cell);
            }
            let results = Array.from(res);
            results.sort(orderNumber);
            for(let row of table.rows) {
                let cell = row.cells[col].innerText;
                let place = results.indexOf(cell) + 1;
                if (1 <= place && place <= 3) row.cells[col].classList.add('p' + place);
            }
        }
    }
}

function getRatingTableElement() {
    return document.getElementById('sorted-table').getElementsByTagName('tbody')[0];
}

function clearRatingTableElement() {
    let table = document.getElementById('sorted-table');
    let tbody = table.getElementsByTagName('tbody')[0];
    let new_tbody = document.createElement('tbody');
    table.replaceChild(new_tbody, tbody);
}

function generateRatingTable(lines, result_col, colorize=true) {
    clearRatingTableElement();
    let place = 0, cnt = 1, lastResult = null, rating_table = getRatingTableElement();
    for (let line of lines) {
        let row = document.createElement('tr'), result = line[result_col];
        if (lastResult !== result) { place = cnt; lastResult = result; }
        ++cnt;
        line[0] = place;
        for (let info of line) {
            let cell = document.createElement('td');
            cell.innerHTML = info;
            row.appendChild(cell);
        }
        rating_table.appendChild(row);
    }
    if (colorize) colorizePlaces();
}

function filterResults(class_col, result_col, colorize=true) {
    if (tableData.length) {
        let n = tableData[0].length;
        if (class_col < 0) class_col += n;
        if (result_col < 0) result_col += n;
    }
    let classes = new Set();
    let checkboxes = document.getElementsByName('class_value');
    for (let checkbox of checkboxes) {
        if (checkbox.checked) classes.add(checkbox.value);
    }
    let new_lines = [];
    for (let line of tableData) {
        let cell = line[class_col];
        if (class_col === null || classes.has(cell)) new_lines.push(line);
    }
    generateRatingTable(new_lines, result_col, colorize);
}

function setChecked(cls, newChecked) {
    let checkboxes = document.getElementsByName('class_value');
    for (let checkbox of checkboxes) {
        let value = checkbox.value;
        if (cls === null || value.includes(cls)) checkbox.checked = newChecked;
    }
}

function generateAllTable() {
    document.getElementById('filter-all').click();
    document.getElementById('filter-do').click();
}


function compareStudentsResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[3] !== b[3]) return a[3].localeCompare(b[3]);
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[2] !== b[2]) return a[2].localeCompare(b[2]);
    return 0;
}

function generateStudentsTableData() {
    let lines = [];
    for (let student_id in students) {
        let line = [], sum = 0;
        let result = student_id in results ? results[student_id] : {};
        line.push(0);
        for (let data of students[student_id]) line.push(data);
        for (let subject_id in subjects) {
            if (subject_id in result) {
                let data = result[subject_id];
                line.push(`${data[0]}&nbsp;(${data[1]})`);
                sum += data[0];
            }
            else line.push('-');
        }
        line.push(sum);
        if (sum > 0) lines.push(line);
    }
    lines.sort(compareStudentsResults);
    return lines;
}


function compareClassesResults(a, b) {
    if (a[2] !== b[2]) return b[2] - a[2];
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[3] !== b[3]) return a[3] - b[3];
    return 0;
}

function generateClassesTableData() {
    let lines = [];
    for (let res of results) {
        let line = [0];
        for (let data of res) line.push(data);
        lines.push(line);
    }
    lines.sort(compareClassesResults);
    return lines;
}


function compareTeamsResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    return 0;
}

function generateTeamsTableData() {
    let lines = [];
    for (let team_id in results) {
        let line = [0, teams[team_id]], sum = 0;
        for (let subject in subjects) {
            if (subject in results[team_id]) {
                line.push(results[team_id][subject]);
                sum += results[team_id][subject];
            } else line.push('-');
        }
        line.push(sum);
        lines.push(line);
    }
    lines.sort(compareTeamsResults);
    return lines;
}
