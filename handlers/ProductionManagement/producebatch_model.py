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
from models.SystemManagement.system import ElectronicBatch
from collections import Counter
from libs.log.BK2TLogger import logger,insertSyslog

engine = create_engine(db_operate.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

produce = Blueprint('produce', __name__)

# 组织机构建模
@produce.route('/ElectronicBatchRecordNav')
def electronicBatchRecord():
    return render_template('./ProductionManagement/electronicBatchRecordNav.html')
@produce.route('/ElectronicBatchRecord')
def ElectronicBatchRecord():
    return render_template('./ProductionManagement/electronicBatchRecord.html')
