import string
from flask import Blueprint, render_template, request, make_response
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine, func, desc
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from dbset.database import db_operate
from dbset.log.BK2TLogger import insertSyslog, MESLogger
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import Organization, SysLog
from collections import Counter
from dbset.log.BK2TLogger import logger,insertSyslog
from tools.common import insert,delete,update
from dbset.database.db_operate import db_session

systemlog = Blueprint('systemlog', __name__, template_folder='templates')

# 系统日志
@systemlog.route('/syslogs')
def syslogs():
    return render_template('syslogs.html')


# 日志查询
@systemlog.route('/syslogs/findByDate')
def syslogsFindByDate():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                startTime = data['startTime']  # 开始时间
                endTime = data['endTime']  # 结束时间
                if startTime == "" and endTime == "":
                    total = db_session.query(SysLog).count()
                    syslogs = db_session.query(SysLog).order_by(desc("OperationDate")).all()[inipage:endpage]
                elif startTime != "" and endTime == "":
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    total = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, nowTime)).count()
                    syslogs = db_session.query(SysLog).filter(
                        SysLog.OperationDate.between(startTime, nowTime)).order_by(desc("OperationDate")).all()[
                              inipage:endpage]
                else:
                    total = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, endTime)).count()
                    syslogs = db_session.query(SysLog).filter(
                        SysLog.OperationDate.between(startTime, endTime)).order_by(desc("OperationDate")).all()[
                              inipage:endpage]
                jsonsyslogs = json.dumps(syslogs, cls=AlchemyEncoder, ensure_ascii=False)
                jsonsyslogs = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonsyslogs + "}"
                return jsonsyslogs
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 插入日志OperationType OperationContent OperationDate UserName ComputerName IP
def insertSyslog(operationType, operationContent, userName):
    try:
        if operationType == None: operationType = ""
        if operationContent == None:
            operationContent = ""
        else:
            operationContent = str(operationContent)
        if userName == None: userName = ""
        ComputerName = socket.gethostname()
        db_session.add(
            SysLog(OperationType=operationType, OperationContent=operationContent,
                   OperationDate=datetime.datetime.now(), UserName=userName,
                   ComputerName=ComputerName, IP=socket.gethostbyname(ComputerName)))
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)