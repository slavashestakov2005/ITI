from backend import app
from .help import check_status, check_block_year
from ..database import MessagesTable
from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required


def page_args(year: int):
    return {'year': abs(year), 'messages': MessagesTable.select_by_year(year)}


@app.route("/<year:year>/subjects_for_year.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subjects_for_year(year: int):
    return render_template(str(year) + '/subjects_for_year.html', **page_args(year))
