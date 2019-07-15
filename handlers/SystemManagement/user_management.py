import json, string, re, datetime
from flask import Blueprint, render_template, request
from dbset.database.db_operate import db_session
from models.SystemManagement.system import Organization,Role,User
from sqlalchemy import and_,desc
from dbset.main.BSFramwork import AlchemyEncoder
from dbset.log.BK2TLogger import logger,insertSyslog
from flask_login import current_user

user_manage = Blueprint('user_manage', __name__, template_folder='templates', url_prefix='/user_manage')

# 用户管理
@user_manage.route('/default')
def userManager():
    departments = db_session.query(Organization.ID, Organization.OrganizationName).all()
    # print(departments)
    # departments = json.dumps(departments, cls=AlchemyEncoder, ensure_ascii=False)
    data = []
    for tu in departments:
        li = list(tu)
        id = li[0]
        name = li[1]
        department = {'OrganizationID':id,'OrganizationName':name}
        data.append(department)

    dataRoleName = []
    roleNames = db_session.query(Role.ID, Role.RoleName).all()
    for role in roleNames:
        li = list(role)
        id = li[0]
        name = li[1]
        roleName = {'RoleID': id, 'RoleName': name}
        dataRoleName.append(roleName)
    return render_template('./SystemManagement/userManager.html', departments=data, roleNames=dataRoleName)
@user_manage.route('/MyUser/Select')
def MyUserSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data.get("offset"))  # 页数
                rowsnumber = int(data.get("limit"))  # 行数
                inipage = pages * rowsnumber + 0  # 起始页
                endpage = pages * rowsnumber + rowsnumber  # 截止页
                id = data.get('id')
                Name = data.get('Name')
                if id != '':
                    OrganizationCodeData = db_session.query(Organization).filter_by(ID=id).first()
                    if OrganizationCodeData != None:
                        OrganizationName = str(OrganizationCodeData.OrganizationName)
                        total = db_session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else "")).count()
                        oclass = db_session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else "")).order_by(desc("CreateTime")).all()[inipage:endpage]
                    else:
                        total = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                        oclass = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").order_by(desc("CreateTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                    oclass = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").order_by(desc("CreateTime")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
            return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询用户列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@user_manage.route('/user/addUser', methods=['POST', 'GET'])
def addUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                user = User()
                user.WorkNumber=data['WorkNumber']
                ocal = db_session.query(User).filter(User.WorkNumber == user.WorkNumber).first()
                if ocal != None:
                    return "工号重复，请重新录入！"
                user.Name=data['Name']
                user.Password=user.password(data['Password'])
                # print(user.Password)
                user.Status="1" # 登录状态先设置一个默认值1：已登录，0：未登录
                user.Creater=current_user.Name
                user.CreateTime=datetime.datetime.now()
                user.LastLoginTime=datetime.datetime.now()
                user.IsLock='false' # data['IsLock'],
                user.OrganizationName=data['OrganizationName']
                user.RoleName=data['RoleName']
                db_session.add(user)
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "添加用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@user_manage.route('/user/updateUser', methods=['POST', 'GET'])
def UpdateUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                id = int(data['ID'])
                user = db_session.query(User).filter_by(id=id).first()
                user.Name = data['Name']
                user.WorkNumber = data['WorkNumber']
                ocal = db_session.query(User).filter(User.WorkNumber == user.WorkNumber).first()
                if ocal != None:
                    if ocal.id != id:
                        return "工号重复，请重新修改！"
                user.Password = user.password(data['Password'])
                # user.Status = data['Status']
                # user.Creater = data['Creater']
                # user.CreateTime = data['CreateTime']
                # user.LastLoginTime = data['LastLoginTime']
                # user.IsLock = data['IsLock']
                user.OrganizationName = data['OrganizationName']
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@user_manage.route('/user/deleteUser', methods=['POST', 'GET'])
def deleteUser():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(User).filter_by(id=id).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        insertSyslog("error", "删除户ID为"+string(id)+"报错Error：" + string(ee), current_user.Name)
                        return json.dumps("删除用户报错", cls=AlchemyEncoder,ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)