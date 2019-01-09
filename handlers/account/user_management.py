from flask import Blueprint, render_template
from libs.database.db_operate import db_session

user_manage = Blueprint('user_manage',__name__, url_prefix='/user_manage')

# 用户管理
@user_manage.route('/userManager')
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
    return render_template('userManager.html',departments=data,roleNames=dataRoleName)