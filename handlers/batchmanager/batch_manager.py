from flask import Blueprint, render_template, request, make_response
import json
from dbset.database.db_operate import db_session
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import BatchIDPUID
from dbset.log.BK2TLogger import logger,insertSyslog
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from tools.common import insert,delete,update

batch = Blueprint('batch', __name__, template_folder='templates')

@batch.route('/ElectronicBatchRecordNav')
def electronicBatchRecord():
    return render_template('./ProductionManagement/electronicBatchRecordNav.html')
# 生产数据管理-电子批记录
@batch.route('/ElectronicBatchRecord', methods=['POST', 'GET'])
def ElectronicBatchRecord():
    if request.method == 'GET':
        data = request.values
        BatchID = data.get('BatchID')
        ocal = db_session.query(BatchIDPUID).filter(BatchIDPUID.BatchID == BatchID).first()
        title = ocal.PUIDName
        return render_template('./ProductionManagement/electronicBatchRecord.html', title = title, BatchID = BatchID)

@batch.route('/BatchIDPUIDSearch', methods=['POST', 'GET'])
def BatchIDPUIDSearch():
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data.get("offset"))
                rowsnumber = int(data.get("limit"))
                inipage = pages * rowsnumber + 0
                endpage = pages * rowsnumber + rowsnumber
                BatchID = data['BatchID']
                if(BatchID == "" or BatchID == None):
                    total = db_session.query(BatchIDPUID).order_by(("BatchID")).count()
                    oclass = db_session.query(BatchIDPUID).order_by(("BatchID")).all()[inipage:endpage]
                else:
                    total = db_session.query(BatchIDPUID).filter(BatchIDPUID.BatchID.like("%" + BatchID + "%")).count()
                    oclass = db_session.query(BatchIDPUID).filter(BatchIDPUID.BatchID.like("%" + BatchID + "%")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)

@batch.route('/BatchIDPUIDCreate', methods=['POST', 'GET'])
def BatchIDPUIDCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return insert(BatchIDPUID, data)

@batch.route('/BatchIDPUIDUpdate', methods=['POST', 'GET'])
def BatchIDPUIDUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return update(BatchIDPUID, data)

@batch.route('/BatchIDPUIDDelete', methods=['POST', 'GET'])
def BatchIDPUIDDelete():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return delete(BatchIDPUID, data)