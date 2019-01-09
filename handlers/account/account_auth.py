import json
from flask import Blueprint, render_template, request, redirect, session, url_for
from libs.database.db_operate import db_session
from libs.log.BK2TLogger import logger
from libs.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import User, Role, Menu, Role_Menu
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from sqlalchemy.exc import InvalidRequestError


#flask_login的初始化
login_manager = LoginManager()
login_manager.db_session_protection = 'strong'
login_manager.login_view ='login'


login_auth = Blueprint('login_auth', __name__, url_prefix='/account')

'''登录'''
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=int(user_id)).first()

@login_auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('./main/login.html')
        if request.method == 'POST':
            data = request.values
            work_number = data['WorkNumber']
            password = data['password']
                # 验证账户与密码
            user = db_session.query(User).filter_by(WorkNumber=work_number).first()
            if user and user.confirm_password(password):
                login_user(user)  # login_user(user)调用user_loader()把用户设置到db_session中
                # 查询用户当前菜单权限
                roles = db_session.query(User.RoleName).filter_by(WorkNumber=work_number).all()
                menus = []
                for role in roles:
                    for index in role:
                        role_id = db_session.query(Role.ID).filter_by(RoleName=index).first()
                        menu = db_session.query(Menu.ModuleCode).join(Role_Menu, isouter=True).filter_by(Role_ID=role_id).all()
                        for li in menu:
                            menus.append(li[0])
                session['menus'] = menus
                return redirect('/')
            # 认证失败返回登录页面
            error = '用户名或密码错误'
            return render_template('./main/login.html', error=error)
    except InvalidRequestError:
        db_session.rollback()
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 退出登录
# 使用login_required装饰路由函数,未登录的请求将会跳转到上面login_manger.login_view设置的登录页面路由
@login_auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))