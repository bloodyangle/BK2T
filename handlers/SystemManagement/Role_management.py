import json
import re, string, datetime
from collections import Counter
from flask import render_template,request,Blueprint
from sqlalchemy import func

from libs.database.db_operate import db_session
from models.SystemManagement.system import Role
from flask_login import current_user
from libs.log.BK2TLogger import logger,insertSyslog
from libs.main.BSFramwork import AlchemyEncoder

role_management = Blueprint('role_management', __name__)

# 工作台菜单role
@role_management.route('/sysrole')
def sysrole():
    dataRoleInfo = []
    roleNames = db_session.query(Role.ID, Role.RoleName).all()
    for role in roleNames:
        li = list(role)
        id = li[0]
        name = li[1]
        roleName = {'RoleID': id, 'RoleName': name}
        dataRoleInfo.append(roleName)
    return render_template('sysRole.html', RoleInfos=dataRoleInfo)


# role更新数据，通过传入的json数据，解析之后进行相应更新
@role_management.route('/allroles/Update', methods=['POST', 'GET'])
def allrolesUpdate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                Roleid = int(data['ID'])
                role = db_session.query(Role).filter_by(ID=Roleid).first()
                role.RoleName = data['RoleName']
                role.RoleSeq = data['RoleSeq']
                role.Description = data['Description']
                role.CreatePerson = data['CreatePerson']
                role.CreateDate = data['CreateDate']
                role.ParentNode = data['ParentNode']
                db_session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新角色报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@role_management.route('/allroles/Delete', methods=['POST', 'GET'])
def allrolesDelete():
    if request.method == 'POST':
        data = request.values
        try:
            #   jsonDict = data.to_dict(
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    Roleid = int(key)
                    try:
                        oclass = db_session.query(Role).filter_by(ID=Roleid).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "删除角色报错Error：" + str(ee), current_user.Name)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除角色报错Error：" + str(e), current_user.Name)
            # return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role创建数据，通过传入的json数据，解析之后进行相应更新
@role_management.route('/allroles/Create', methods=['POST', 'GET'])
def allrolesCreate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(Role(RoleName=data['RoleName'],
                                 RoleSeq=data['RoleSeq'],
                                 Description=data['Description'],
                                 CreatePerson=data['CreatePerson'],
                                 CreateDate= datetime.datetime.now(),
                                 ParentNode = data['ParentNode']
                                 ))
                db_session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "创建角色报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:"+ str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


#role查询数据，通过传入的json数据，解析之后进行相应更新
#采用服务端数据分页，通过easyui-datagrid传入的页数和每页包含的记录数回传
#注意写easyui-datagrid的json数据格式！特别是最开始部分"total":20,"rows":[]}
@role_management.route('/allroles/Find')
def allrolesFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(func.count(Role.ID)).scalar()
                roles = db_session.query(Role).all()[inipage:endpage]
                # ORM模型转换json格式
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@role_management.route('/allroles/Search', methods=['POST', 'GET'])
def allrolesSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                roles = db_session.query(Role).filter(Role.RoleName.like(strconditon)).all()
                total = Counter(roles)
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "擦护心角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
