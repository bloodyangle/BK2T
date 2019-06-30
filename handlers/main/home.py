from flask import Blueprint, render_template
from flask_login import login_required


home_page = Blueprint('home_page', __name__, template_folder='templates')


# 加载工作台
@home_page.route('/workbench')
def workbenck():
    return render_template('./main/workbench.html')