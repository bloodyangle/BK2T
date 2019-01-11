import string
from flask import Blueprint, render_template, request, make_response
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine, func
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from libs.database import db_operate
from libs.log.BK2TLogger import insertSyslog, MESLogger
from libs.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import Organization
from collections import Counter
from libs.log.BK2TLogger import logger,insertSyslog

engine = create_engine(db_operate.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

organiza = Blueprint('organiza', __name__)

# 组织机构建模
@organiza.route('/organization')
def organization():
    return render_template('./SystemManagement/sysOrganization.html')

@organiza.route('/allOrganizations/Find')
def OrganizationsFind():
    if request.method == 'GET':
        data = request.values # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page']) # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber #截止页
                db_operate.FuzzyQuery(Organization, Organization.OrganizationName)
                total = db_session.query(func.count(Organization.ID)).scalar()
                organiztions = db_session.query(Organization).all()[inipage:endpage]
                #ORM模型转换json格式
                jsonorganzitions = json.dumps(organiztions, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganzitions = '{"total"'+":"+str(total)+',"rows"' +":\n" + jsonorganzitions + "}"
                return jsonorganzitions
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:"+ str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# role更新数据，通过传入的json数据，解析之后进行相应更新
@organiza.route('/allOrganizations/Update', methods=['POST', 'GET'])
def allOrganizationsUpdate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                organizationid = int(data['ID'])
                organization = db_session.query(Organization).filter_by(ID=organizationid).first()
                organization.OrganizationCode = data['OrganizationCode']
                organization.OrganizationName = data['OrganizationName']
                organization.ParentCode = data['ParentNode']
                organization.OrganizationSeq = data['OrganizationSeq']
                organization.Description = data['Description']
                organization.CreatePerson = data['CreatePerson']
                organization.CreateDate = data['CreateDate']
                organization.Img = data['Img']
                organization.Color = data['Color']
                db_session.commit()
                return json.dumps(['OK'], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@organiza.route('/allOrganizations/Delete', methods=['POST', 'GET'])
def allOrganizationsDelete():
    if request.method == 'POST':
        data = request.values
        try:
            #   jsonDict = data.to_dict(
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    Organizationid = int(key)
                    try:
                        oclass = db_session.query(Organization).filter_by(ID=Organizationid).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "删除组织报错Error：" + str(ee), current_user.Name)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps(['OK'], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除组织报错Error：" + str(e), current_user.Name)
            # return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role创建数据，通过传入的json数据，解析之后进行相应更新
@organiza.route('/allOrganizations/Create', methods=['POST', 'GET'])
def allOrganizationsCreate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                if data['Img'] == "":
                    DspImg = "antonio.jpg"
                else:
                    DspImg = data['Img']

                if data['Color'] == "":
                    DspColor = "#1696d3"
                else:
                    DspColor = data['Color']
                db_session.add(
                    Organization(OrganizationCode=data['OrganizationCode'],
                                 OrganizationName=data['OrganizationName'],
                                 ParentNode=data['ParentNode'],
                                 OrganizationSeq=data['OrganizationSeq'],
                                 Description=data['Description'],
                                 CreatePerson=data['CreatePerson'],
                                 CreateDate=datetime.datetime.now(),Img = DspImg,Color = DspColor))
                db_session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "新增组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@organiza.route('/allOrganizations/Search', methods=['POST', 'GET'])
def allOrganizationsSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                organizations = db_session.query(Organization).filter(Organization.OrganizationName.like(strconditon)).all()
                total = Counter(organizations)
                jsonorganizations = json.dumps(organizations, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganizations = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonorganizations + "}"
                return jsonorganizations
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@organiza.route('/organizationMap')
def organizationMap():
    return render_template('./SystemManagement/index_organization.html')

@organiza.route('/organizationMap/selectAll')#组织结构
def selectAll():
    if request.method == 'GET':
        try:
            data = getMyOrganizationChildrenMap(id=0)
            jsondata = [{"name":"北京康仁堂","value":"0","children":data}]
            jsondatas = json.dumps(jsondata, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondatas
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
                sz.append({"id": obj.ID, "text": obj.OrganizationName, "children": getMyOrganizationChildren(obj.ID)})
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
        # data = string(sz)"'"
        # data.replace(srep, '')
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
            # data = load()
            data = getMyOrganizationChildren(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@organiza.route('/Myenterprise')
def myenterprise():
    if request.method == 'GET':
        try:
            # data = load()
            data = getMyEnterprise(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@organiza.route('/Myenterprise/Select')
def MyenterpriseSelect():
    if request.method == 'GET':
        odata = request.values
        try:
            json_str = json.dumps(odata.to_dict())
            if len(json_str) > 5:
                objid = int(odata['ID'])
                oclass = db_session.query(Organization).filter_by(ID=objid).first()
                jsondata = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
