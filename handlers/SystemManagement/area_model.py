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

logger = MESLogger('../logs', 'log')
engine = create_engine(db_operate.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

area = Blueprint('area', __name__)
# 加载工作台
@area.route('/Area')
def getRootArea():
    return render_template('sysArea.html')


@area.route('/allAreas/Find')
def AreasFind():
    if request.method == 'GET':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaFind")
        re = AreaIFS.AreasFind(data)
        logger.info(re)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@area.route('/allAreas/Update', methods=['POST', 'GET'])
def allAreasUpdate():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaUpdate")
        re = AreaIFS.allAreasUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@area.route('/allAreas/Delete', methods=['POST', 'GET'])
def allAreasDelete():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaDelete")
        re = AreaIFS.allAreasDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@area.route('/allAreas/Create', methods=['POST', 'GET'])
def allAreasCreate():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaCreate")
        re = AreaIFS.allAreasCreate(data)
        return re


@area.route('/allAreas/Search', methods=['POST', 'GET'])
def allAreasSearch():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaSearch")
        re = AreaIFS.allAreasSearch(data)
        return re
