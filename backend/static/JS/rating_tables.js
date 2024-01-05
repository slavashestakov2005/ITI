function colorizePlaces() {
    let tables = document.getElementsByClassName('js-table-color-place');
    for(let table of tables) {
        for(let row of table.rows) {
            let elem = row.cells[0];
            if (elem === undefined) continue;
            let cell = elem.innerText;
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

function generateRatingTable(lines, result_col, colorize=true, clss=[]) {
    clearRatingTableElement();
    let place = 0, cnt = 1, lastResult = null, rating_table = getRatingTableElement();
    for (let line of lines) {
        let row = document.createElement('tr'), result = line[result_col];
        if (clss.length) for (let cls of clss) row.classList.add(cls);
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

function filterResults(school_col, class_col, result_col, do_filter=true, colorize=true, clss=[]) {
    if (tableData.length) {
        let n = tableData[0].length;
        if (school_col < 0) school_col += n;
        if (class_col < 0) class_col += n;
        if (result_col < 0) result_col += n;
    }
    let new_lines = [];
    if (do_filter) {
        let classes = new Set();
        let checkboxes = document.getElementsByName('class_value');
        for (let checkbox of checkboxes) {
            if (checkbox.checked) classes.add(checkbox.value);
        }
        for (let line of tableData) {
            let cell_school = line[school_col];
            let cell_class = line[class_col];
            let cell_data = cell_school + '|' + cell_class[0] + '|' + cell_class.slice(1);
            if (classes.has(cell_data)) new_lines.push(line);
        }
    } else {
        new_lines = tableData;
    }
    generateRatingTable(new_lines, result_col, colorize, clss);
}

function setChecked(school, number, letter, newChecked) {
    let checkboxes = document.getElementsByName('class_value');
    for (let checkbox of checkboxes) {
        let data = checkbox.value.split('|');
        if ((school === null || school === data[0]) &&
            (number === null || number === data[1]) &&
            (letter === null || letter === data[2])) {
                checkbox.checked = newChecked;
        }
    }
    doAutoFilter();
}

function generateAllTable() {
    document.getElementById('filter-all').click();
    document.getElementById('filter-do').click();
}

function generateNoneTable() {
    document.getElementById('filter-none').click();
    document.getElementById('filter-do').click();
}

function doAutoFilter() {
    if (pre_filter) pre_filter();
    document.getElementById('filter-do').click();
}

function initAutoFilter(class_name) {
    let elements = document.getElementsByTagName('input');
    for (let pos in elements){
        let current = elements[pos];
        if (current.type === 'checkbox' && current.name === class_name) {
            current.addEventListener('click', doAutoFilter);
        }
    }
}

// rating_students.html

function compareStudentsResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[3] !== b[3]) return a[3].localeCompare(b[3]);
    if (a[4] !== b[4]) return a[4].localeCompare(b[4]);
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[2] !== b[2]) return a[2].localeCompare(b[2]);
    return 0;
}

function generateStudentsTableData(addCheckBoxes=false) {
    let lines = [];
    for (let student_id in students) {
        let line = [], sum = {};
        let result = student_id in results ? results[student_id] : {};
        line.push(0);
        for (let data of students[student_id]) line.push(data);
        for (let sub of subjects) {
            let subject_id = sub[0];
            if (subject_id in result) {
                let data = result[subject_id];
                line.push(`${data[0]}&nbsp;(${data[1]})`);
                let day = subjects_days[subject_id];
                if (!(day in sum)) {
                    sum[day] = [];
                }
                sum[day].push(data[0]);
            }
            else line.push('—');
        }
        let all_sum = 0;
        if (student_id in students_group_result) {
            let st_res = students_group_result[student_id];
            line.push(st_res);
            if (st_res.includes('баллов')) {
                let val = st_res.split('баллов')[0].split('(')[1];
                all_sum += parseFloat(val);
            }
        }
        else line.push('');
        if (addCheckBoxes) line.push(student_id);
        for (day in sum) {
            let sorted = sum[day].sort((a, b) => (b - a)).splice(0, ind_res_per_day);
            let day_sum = sorted.reduce((partialSum, a) => partialSum + a, 0);
            all_sum += day_sum
        }
        line.push(all_sum);
        lines.push(line);
    }
    lines.sort(compareStudentsResults);
    return lines;
}

// rating_students_check.html

function addCheckBoxes() {
    let rating_table = getRatingTableElement();
    let plus_count = 0, minus_count = 0;
    for (let row of rating_table.rows) {
        let n = row.cells.length;
        let student_id = row.cells[n - 2].innerText;
        let cell = document.createElement('td');
        let template = '<input class="js-rating-check" type="checkbox" name="t" value="000_0" id="000_0">-<input type="checkbox" name="ot" value="000_0" id="000_0_old" hidden>\n' +
                         '<input class="js-rating-check" type="checkbox" name="t" value="000_1" id="000_1">?<input type="checkbox" name="ot" value="000_1" id="000_1_old" hidden>\n' +
                         '<input class="js-rating-check" type="checkbox" name="t" value="000_2" id="000_2">+<input type="checkbox" name="ot" value="000_2" id="000_2_old" hidden>\n';
        template = template.replace(/000/g, student_id);
        cell.innerHTML = template;
        if (student_id in checkMarks) {
            if (checkMarks[student_id] === 1) {
                ++plus_count;
                cell.children[4].checked = true;
                cell.children[5].checked = true;
            } else {
                ++minus_count;
                cell.children[0].checked = true;
                cell.children[1].checked = true;
            }
        } else {
            cell.children[2].checked = true;
            cell.children[3].checked = true;
        }
        row.appendChild(cell);
    }
    document.getElementById("rating_students_check_plus").innerHTML = plus_count;
    document.getElementById("rating_students_check_minus").innerHTML = minus_count;
}

// rating_classes.html

function compareClassesResults(a, b) {
    if (a[2] !== b[2]) return b[3] - a[3];
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[2] !== b[2]) return a[2].localeCompare(b[2]);
    if (a[3] !== b[3]) return a[4] - b[4];
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

// rating_teams.html

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
        for (let sub of subjects) {
            let subject = sub[0];
            if (subject in results[team_id]) {
                if (subject < 0) {
                    line.push(results[team_id][subject][0]);
                    sum += results[team_id][subject][0];
                } else {
                    line.push(results[team_id][subject][0] * results[team_id][subject][1]);
                    sum += results[team_id][subject][0] * results[team_id][subject][1];
                }
            } else line.push('-');
        }
        line.push(sum);
        lines.push(line);
    }
    lines.sort(compareTeamsResults);
    return lines;
}

// rating.html

function compareSuperChampionResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[3] !== b[3]) return a[3].localeCompare(b[3]);
    if (a[4] !== b[4]) return a[4].localeCompare(b[4]);
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    return a[2].localeCompare(b[2]);
}

function generateSuperChampionTableData() {
    let lines = [];
    for (let student_id in results) {
        let line = [0], sum = '';
        for (let data of students[student_id]) line.push(data);
        for (let data of results[student_id]) {
            sum += data;
            line.push(data);
        }
        line.push(sum);
        lines.push(line);
    }
    lines.sort(compareSuperChampionResults);
    return lines.slice(0, 20);
}

// for many pages

function preparePageForConvert() {
    for (let elem of document.getElementsByClassName('js-table-for-excel-head-main')) {
        elem.setAttribute('style', 'display:none');
        for (let cell of elem.cells) {
            cell.setAttribute('data-f-sz', '20');
            cell.setAttribute('data-f-bold', 'true');
            cell.setAttribute('data-a-h', 'center');
        }
    }
    for (let elem of document.getElementsByClassName('js-table-for-excel-head-sub')) {
        for (let cell of elem.cells) {
            cell.setAttribute('data-b-a-s', 'thin');
            cell.setAttribute('data-f-sz', '14');
            cell.setAttribute('data-a-wrap', 'true');
            cell.setAttribute('data-f-bold', 'true');
        }
    }
    for (let elem of document.getElementsByClassName('js-table-for-excel-body')) {
        let color = null;
        if (elem.classList.contains("p1")) color = 'ffffd70';
        if (elem.classList.contains("p2")) color = 'ffc0c0c0';
        if (elem.classList.contains("p3")) color = 'ffefa540';
        for (let cell of elem.cells) {
            cell.setAttribute('data-b-a-s', 'thin');
            cell.setAttribute('data-f-sz', '14');
            if (color !== null) cell.setAttribute('data-fill-color', color);
        }
    }
}

TableToExcel.convert_many = function(file_name, data=[]) {
    let opts = {
        name: file_name + ".xlsx",
        autoStyle: false,
        sheet: {
            name: "default name"
        }
    };
    let wb = TableToExcel.initWorkBook();
    for (let page of data) {
        let name = page[0], table = page[1];
        opts.sheet.name = name;
        wb = TableToExcel.tableToSheet(wb, table, opts);
    }
    TableToExcel.save(wb, opts.name);
};

// subject_ind.html

function getSubjectExcel(year, subject) {
    let data = [], file_name = 'ИТИ ' + year + '. ' + subject;
    for (let cls of classes) {
        data.push([cls + ' класс', document.getElementById('table-c' + cls)]);
    }
    TableToExcel.convert_many(file_name, data);
}

// rating_classes.html

function getClassTable() {
    preparePageForConvert();
    return document.getElementById('sorted-table').cloneNode(true);
}

function getClassesExcel(year) {
    let data = [], file_name = 'ИТИ ' + year + '. Результаты классов';
    let filter_all = document.getElementById("filter-all"), filter_none = document.getElementById("filter-none"),
        filter_do = document.getElementById("filter-do"), table_name = document.getElementById('table-head-content');
    filter_all.click();
    filter_do.click();
    table_name.innerHTML = 'Общий';
    data.push(['Общий', getClassTable()]);
    for (let cls of classes) {
        let name = cls + ' класс';
        table_name.innerHTML = name;
        filter_none.click();
        setChecked(null, cls, null, true);
        data.push([name, getClassTable()]);
    }
    filter_all.click();
    filter_do.click();
    TableToExcel.convert_many(file_name, data);
    table_name.innerHTML = '';
}
