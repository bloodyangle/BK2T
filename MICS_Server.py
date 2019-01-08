from flask import Flask
from libs.account import auth_lib
from handlers.account import account_auth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qeqhdasdqiqd131'
account_auth.login_manager.init_app(app)

# 将后台函数传到前端
app.add_template_global(account_auth.isIn, 'isIn')

app.register_blueprint(account_auth)

@app.route('/')
def index():
    return 'hello world'

if __name__ == "__main__":
    app.run(debug=True)