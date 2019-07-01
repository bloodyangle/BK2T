import string
from flask import Blueprint, render_template, request, make_response
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine, func
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from dbset.database import db_operate
from dbset.log.BK2TLogger import insertSyslog, MESLogger
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import Organization
from collections import Counter
from dbset.log.BK2TLogger import logger,insertSyslog
from tools.common import insert,delete,update
from dbset.database.db_operate import db_session

organiza = Blueprint('organiza', __name__, template_folder='templates')

# 组织机构建模
@organiza.route('/organization')
def organization():
    return render_template('./SystemManagement/sysOrganization.html')

@organiza.route('/OrganizationSelect')
def OrganizationSelect():
    if request.method == 'GET':
        data = request.values # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data.get("offset"))  # 页数
                rowsnumber = int(data.get("limit"))  # 行数
                inipage = pages * rowsnumber + 0  # 起始页
                endpage = pages * rowsnumber + rowsnumber  # 截止页
                OrganizationName = data.get("OrganizationName")
                if OrganizationName == None or OrganizationName == "":
                    total = db_session.query(func.count(Organization.ID)).scalar()
                    organiztions = db_session.query(Organization).all()[inipage:endpage]
                else:
                    total = db_session.query(Organization.ID).filter(Organization.OrganizationName.like("%"+OrganizationName+"%")).all()
                    organiztions = db_session.query(Organization).filter(Organization.OrganizationName.like("%"+OrganizationName+"%")).all()[inipage:endpage]
                jsonorganzitions = json.dumps(organiztions, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"'+":"+str(total)+',"rows"' +":\n" + jsonorganzitions + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:"+ str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
@organiza.route('/OrganizationCreate', methods=['GET', 'POST'])
def OrganizationCreate():
    if request.method == 'POST':
        data = request.values
        return insert(Organization, data)
@organiza.route('/OrganizationUpdate', methods=['GET', 'POST'])
def OrganizationUpdate():
    if request.method == 'POST':
        data = request.values
        return update(Organization, data)
@organiza.route('/OrganizationDelete', methods=['GET', 'POST'])
def OrganizationDelete():
    if request.method == 'POST':
        data = request.values
        return delete(Organization, data)
@organiza.route('/organizationMap')
def organizationMap():
    return render_template('./SystemManagement/index_organization.html')

@organiza.route('/organizationMap/selectAll')#组织结构
def selectAll():
    if request.method == 'GET':
        try:
            return json.dumps(getMyOrganizationChildrenMap(id=0), cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            insertSyslog("error", "查询组织结构报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
def getMyOrganizationChildrenMap(id):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append(
                    {"name": obj.OrganizationName, "value": obj.ID, "children": getMyOrganizationChildrenMap(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@organiza.route('/Myorganization')
def myorganization():
    return render_template('./SystemManagement/Myorganization.html')
def getMyOrganizationChildren(id=0):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.OrganizationName, "nodes": getMyOrganizationChildren(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
def getMyEnterprise(id=0):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            sz.append({"id": obj.ID, "text": obj.OrganizationName, "group": obj.ParentNode})
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "获取树形结构报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
@organiza.route('/MyOp')
def MyOpFind():
    if request.method == 'GET':
        try:
            data = getMyOP(id=0)
            return json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
def getMyOP(id):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append(
                    {"text": obj.OrganizationName, "value": obj.ID, "nodes": getMyOP(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@organiza.route('/Myenterprise')
def myenterprise():
    if request.method == 'GET':
        try:
            return json.dumps(getMyEnterprise(id=0), cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)