import json
from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbset.log.BK2TLogger import logger
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import User, Role, Menu, Role_Menu
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from sqlalchemy.exc import InvalidRequestError
from dbset.database.db_operate import db_session

#flask_login的初始化
login_manager = LoginManager()
login_manager.db_session_protection = 'strong'
login_manager.login_view = 'login_auth.login'

login_auth = Blueprint('login_auth', __name__, template_folder='templates')

'''登录'''
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=int(user_id)).first()

@login_auth.route('/account/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('./main/login.html')
        if request.method == 'POST':
            data = request.values
            work_number = data.get('WorkNumber')
            password = data.get('password')
                # 验证账户与密码
            user = db_session.query(User).filter_by(WorkNumber=work_number).first()
            if user and (user.confirm_password(password) or user.Password == password):
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
@login_auth.route('/account/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_auth.login'))