from flask import Blueprint, render_template, request, make_response
import json
from dbset.database.db_operate import db_session
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import BatchIDPUID
from dbset.log.BK2TLogger import logger,insertSyslog
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from tools.common import insert,delete,update

batch_manager = Blueprint('batch_manager', __name__, template_folder='templates')

@batch_manager.route('/batch_manager')
def batch_manager():
    return render_template('./batch_manager/batch_manager.html')
@batch_manager.route('/BatchIDPUIDSearch', methods=['POST', 'GET'])
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

@batch_manager.route('/BatchIDPUIDCreate', methods=['POST', 'GET'])
def BatchIDPUIDCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return insert(BatchIDPUID, data)

@batch_manager.route('/BatchIDPUIDUpdate', methods=['POST', 'GET'])
def BatchIDPUIDUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return update(BatchIDPUID, data)

@batch_manager.route('/BatchIDPUIDDelete', methods=['POST', 'GET'])
def BatchIDPUIDDelete():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return delete(BatchIDPUID, data)