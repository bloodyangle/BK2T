import json
import re
from flask import render_template,request,Blueprint,redirect,url_for
from dbset.database.db_operate import db_session
from models.SystemManagement.system import Role_Menu,Role,User,Menu
from flask_login import current_user
from dbset.log.BK2TLogger import logger,insertSyslog
from dbset.main.BSFramwork import AlchemyEncoder

permission_distribution = Blueprint('permission_distribution', __name__, template_folder='templates')

# 权限分配
@permission_distribution.route('/roleright')
def roleright():
    return render_template('./SystemManagement/roleRight.html')

# 角色列表树形图
def getRoleList(id=0):
    sz = []
    try:
        roles = db_session.query(Role).filter().all()
        for obj in roles:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID,
                           "text": obj.RoleName,
                           "children": getRoleList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'

        return sz
    except Exception as e:
        print(e)
        insertSyslog("error", "查询角色报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配下的角色列表
@permission_distribution.route('/Permission/SelectRoles')
def SelectRoles():
    if request.method == 'GET':
        try:
            data = getRoleList(id=0)
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询权限分配下的角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 权限分配下的用户列表
@permission_distribution.route('/permission/userlist')
def userList():
    # 获取用户列表
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        # 默认返回所有用户
        ID = data['ID']
        if ID == '':
            try:
                json_str = json.dumps(data.to_dict())
                if len(json_str) > 10:
                    pages = int(data.get("offset"))  # 页数
                    rowsnumber = int(data.get("limit"))  # 行数
                    inipage = pages * rowsnumber + 0  # 起始页
                    endpage = pages * rowsnumber + rowsnumber  # 截止页
                    total = db_session.query(User).count()
                    users_data = db_session.query(User)[inipage:endpage]
                    # ORM模型转换json格式
                    jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                    jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                    return jsonusers.encode("utf8")
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "查询权限分配下的用户列表报错Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
        if ID != '':
            data = request.values  # 返回请求中的参数和form
            try:
                json_str = json.dumps(data.to_dict())
                if len(json_str) > 10:
                    pages = int(data['page'])  # 页数
                    rowsnumber = int(data['rows'])  # 行数
                    inipage = (pages - 1) * rowsnumber + 0  # 起始页
                    endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                    # 通过角色ID获取当前角色对应的用户
                    role_id = data['ID']
                    role_name= db_session.query(Role.RoleName).filter_by(ID=role_id).first()
                    if role_name is None:  # 判断当前角色是否存在
                        return
                    total = db_session.query(User).filter_by(RoleName=role_name).count()
                    users_data = db_session.query(User).filter_by(RoleName=role_name).all()[
                                 inipage:endpage]
                    # ORM模型转换json格式
                    jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                    jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                    return jsonusers
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "通过点击角色查询用户报错Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

def trueOrFalse(obj,role_menus):
    if str(obj.ModuleName) in role_menus:
        return True
    return False

# 权限分配下的功能模块列表
def getMenuList(role_menus, id=0):
    sz = []
    try:
        menus = db_session.query(Menu).filter_by(ParentNode=id).all()
        for obj in menus:
            if obj.ParentNode == id:
                    sz.append({"id": obj.ID,
                               "text": obj.ModuleName,
                               "checked": trueOrFalse(obj, role_menus),
                               "children": getMenuList(role_menus, obj.ID)})
        return sz
    except Exception as e:
        print(e)
        insertSyslog("error", "查询权限分配下的功能模块列表Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载菜单列表
@permission_distribution.route('/permission/menulist')
def menulist():
    if request.method == 'GET':
        role_data = request.values
        if 'id' not in role_data.keys():
            try:
                data = getMenuList(role_menus=[],id=0)
                jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
                return jsondata.encode("utf8")
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "加载菜单列表Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
        id = role_data['id']
        try:
            role_menus = db_session.query(Menu.ModuleName).join(Role_Menu, isouter=True).filter_by(Role_ID=id).all()
            r_menus = []
            for menu in role_menus:
                r_menus.append(menu[0])
            menus_data = getMenuList(r_menus, id=0)
            jsondata = json.dumps(menus_data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "加载菜单列表Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配下为角色添加权限
@permission_distribution.route('/permission/MenuToRole')
def menuToUser():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            # 获取菜单和用户并存入数据库
            role_id = data['role_id']  # 获取角色ID
            if role_id is None:
                return
            menus = db_session.query(Menu).join(Role_Menu, isouter=True).filter_by(Role_ID=id).all()
            if menus:
                db_session.delete(menus)
                db_session.commit()
            menu_id = data['menu_id'] # 获取菜单ID
            if menu_id is None:
                return
            menu_id = re.findall(r'\d+\.?\d*', menu_id)
            for r in menu_id:
                role = db_session.query(Role).filter_by(ID=role_id).first()
                menu = db_session.query(Menu).filter_by(ID=r).first()
                # 将菜单ID和角色ID存入User_Role
                menu.roles.append(role)
                db_session.add(menu)
                db_session.commit()
            # 存入数据库后跳转到权限分配页面
            return redirect(url_for("roleright"))
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "权限分配下为角色添加权限Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)