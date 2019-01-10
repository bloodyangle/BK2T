from flask import Flask, render_template, redirect
from libs.account import auth_lib
from handlers.account import account_auth,user_management
from handlers.main import home
from handlers.account.account_auth import login_required
from handlers.SystemManagement.organization_model import organiza



app = Flask(__name__)
app.config['SECRET_KEY'] = 'qeqhdasdqiqd131'
account_auth.login_manager.init_app(app)

# 将后台函数传到前端
app.add_template_global(auth_lib.isIn, 'isIn')

app.register_blueprint(account_auth.login_auth)
app.register_blueprint(user_management.user_manage)
app.register_blueprint(home.home_page)
#组织结构
app.register_blueprint(organiza)

@app.route('/')
# @login_required
def hello_world():
    return redirect('/home')

if __name__ == "__main__":
    app.run(debug=True)
