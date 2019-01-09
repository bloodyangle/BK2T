from flask import Blueprint, render_template
from flask_login import login_required


home = Blueprint('home', __name__)

@home.route('/')
@login_required
def hello_world():
    return render_template('./main/main.html')


# 加载工作台
@home.route('/workbench')
def workbenck():
    return render_template('workbench.html')