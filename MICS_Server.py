from flask import Flask
from libs.account import auth_lib
from handlers.account import account_auth
from handlers.main import home
from handlers.SystemManagement.organization_model import organiza

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qeqhdasdqiqd131'
account_auth.login_manager.init_app(app)

# 将后台函数传到前端
app.add_template_global(auth_lib.isIn, 'isIn')

# app.register_blueprint(account_auth.login_auth)
app.register_blueprint(home.home_page)

# 系统管理的组织结构蓝图
app.register_blueprint(organiza)

@app.route('/')
def index():
    return 'hello world'

if __name__ == "__main__":
    app.run(debug=True)
