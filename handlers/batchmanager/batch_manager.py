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

# 所有工艺段保存查询操作
@batch.route('/allUnitDataMutual', methods=['POST', 'GET'])
def allUnitDataMutual():
    if request.method == 'POST':
        data = request.values
        data = data.to_dict()
        try:
            for key in data.keys():
                if key == "PUIDName":
                    continue
                if key == "BatchID":
                    continue
                val = data.get(key)
                addUpdateEletronicBatchDataStore(data.get("PUIDName"), data.get("BatchID"), key, val)
            return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "所有工艺段保存查询操作报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder,ensure_ascii=False)
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PUID = data['PUID']
                BatchID = data['BatchID']
                oclasss = db_session.query(BatchIDPUID).filter(BatchIDPUID.PUID == PUID,
                                                               BatchIDPUID.BatchID == BatchID).all()
                dic = {}
                for oclass in oclasss:
                    dic[oclass.Content] = oclass.OperationpValue
            return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "所有工艺段保存查询操作报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder,ensure_ascii=False)
def addUpdateEletronicBatchDataStore(PUIDName, BatchID, ke, val):
    try:
        oc = db_session.query(BatchIDPUID).filter(BatchIDPUID.PUIDName == PUIDName,
                                                  BatchIDPUID.BatchID == BatchID,
                                                  BatchIDPUID.Content == ke).first()
        if oc == None:
            db_session.add(BatchIDPUID(BatchID=BatchID, PUIDName=PUIDName, Content=ke, OperationpValue=val,Operator=current_user.Name))
        else:
            oc.Content = ke
            oc.OperationpValue = val
            oc.Operator = current_user.Name
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        insertSyslog("error", "保存更新EletronicBatchDataStore报错：" + str(e), current_user.Name)
        return json.dumps("保存更新EletronicBatchDataStore报错", cls=AlchemyEncoder,ensure_ascii=False)