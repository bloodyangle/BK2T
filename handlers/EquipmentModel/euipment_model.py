import xlwt
from flask import Blueprint, render_template
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine
from flask import render_template, request, make_response
from dbset.main.BSFramwork import AlchemyEncoder
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from sqlalchemy import create_engine, Column, ForeignKey, Table, Integer, String, and_, or_, desc,extract
from io import StringIO
import calendar
from dbset.main.BSFramwork import AlchemyEncoder
from dbset.database import db_operate
from models.SystemManagement.system import Equipment
from dbset.log.BK2TLogger import logger,insertSyslog
from tools.common import insert,delete,update
from dbset.database.db_operate import db_session

 # 创建蓝图 第一个参数为蓝图的名字
equip = Blueprint('equip', __name__, template_folder='templates')

# 设备建模
@equip.route('/Equipment')
def equipment():
    return render_template('./Equipment/sysEquipment.html')

# 设备建模查询
@equip.route('/allEquipments/Search', methods=['POST', 'GET'])
def allEquipmentsSearch():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data.get("offset"))  # 页数
                rowsnumber = int(data.get("limit"))  # 行数
                inipage = pages * rowsnumber + 0  # 起始页
                endpage = pages * rowsnumber + rowsnumber  # 截止页
                EQPName = data['EQPName']  # 设备名称
                if(EQPName == "" or EQPName == None):
                    total = db_session.query(Equipment).count()
                    pequipments = db_session.query(Equipment).all()[inipage:endpage]
                else:
                    total = db_session.query(Equipment).filter(Equipment.EQPName.like("%" + EQPName + "%")).count()
                    pequipments = db_session.query(Equipment).filter(Equipment.EQPName.like("%" + EQPName + "%")).all()[inipage:endpage]
                jsonpequipments = json.dumps(pequipments, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonpequipments + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)

# 设备建模增加
@equip.route('/allEquipments/Create', methods=['POST', 'GET'])
def equipmentCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return insert(Equipment, data)

# 设备建模修改
@equip.route('/allEquipments/Update', methods=['POST', 'GET'])
def equipmentUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return update(Equipment, data)

# 设备建模删除
@equip.route('/allEquipments/Delete', methods=['POST', 'GET'])
def equipmentDelete():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return delete(Equipment, data)

# 设备建模删除
@equip.route('/aa', methods=['POST', 'GET'])
def aa():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        re = FuzzyQuery(Equipment, data)
        print(re)
        return re