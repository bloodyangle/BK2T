import redis
from flask import Blueprint, render_template, request, make_response
import json
from dbset.database.db_operate import db_session,pool
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import BatchInfoDetail, EletronicBatchDataStore, Equipment, BatchType, \
    ElectronicBatchTwo, BatchInfo
from dbset.log.BK2TLogger import logger,insertSyslog
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from tools.common import insert,delete,update
from dbset.database import constant

batch = Blueprint('batch', __name__, template_folder='templates')

@batch.route('/ElectronicBatchRecordNav')
def electronicBatchRecord():
    return render_template('./ProductionManagement/electronicBatchRecordNav.html')
# 生产数据管理-电子批记录
@batch.route('/ElectronicBatchRecord', methods=['POST', 'GET'])
def ElectronicBatchRecord():
    if request.method == 'GET':
        data = request.values
        BatchNum = data.get('BatchID')
        title = data.get('title')
        ocal = db_session.query(BatchInfoDetail).filter(BatchInfoDetail.BatchNum == BatchNum).first()
        if title == "浓缩":
            title == "浓缩"
        else:
            title = ocal.PUIDName
        return render_template('./ProductionManagement/electronicBatchRecord.html', title = title, BatchNum = BatchNum)

@batch.route('/BatchInfoSearch', methods=['POST', 'GET'])
def BatchInfoSearch():
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data.get("offset"))
                rowsnumber = int(data.get("limit"))
                inipage = pages * rowsnumber + 0
                endpage = pages * rowsnumber + rowsnumber
                BatchNum = data.get('BatchNum')
                if(BatchNum == "" or BatchNum == None):
                    total = db_session.query(BatchInfo).order_by(("BatchNum")).count()
                    oclass = db_session.query(BatchInfo).order_by(("BatchNum")).all()[inipage:endpage]
                else:
                    total = db_session.query(BatchInfo).filter(BatchInfo.BatchNum.like("%" + BatchNum + "%")).count()
                    oclass = db_session.query(BatchInfo).filter(BatchInfo.BatchNum.like("%" + BatchNum + "%")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)

@batch.route('/BatchInfoCreate', methods=['POST', 'GET'])
def BatchInfoCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return insert(BatchInfo, data)

@batch.route('/BatchInfoUpdate', methods=['POST', 'GET'])
def BatchInfoUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return update(BatchInfo, data)

@batch.route('/BatchInfoDelete', methods=['POST', 'GET'])
def BatchInfoDelete():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return delete(BatchInfo, data)

@batch.route('/BatchInfoDetailSearch', methods=['POST', 'GET'])
def BatchInfoDetailSearch():
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data.get("offset"))
                rowsnumber = int(data.get("limit"))
                inipage = pages * rowsnumber + 0
                endpage = pages * rowsnumber + rowsnumber
                BatchNum = data['BatchNum']
                if(BatchNum == "" or BatchNum == None):
                    total = db_session.query(BatchInfoDetail).order_by(("BatchNum")).count()
                    oclass = db_session.query(BatchInfoDetail).order_by(("BatchNum")).all()[inipage:endpage]
                else:
                    total = db_session.query(BatchInfoDetail).filter(BatchInfoDetail.BatchNum.like("%" + BatchNum + "%")).count()
                    oclass = db_session.query(BatchInfoDetail).filter(BatchInfoDetail.BatchNum.like("%" + BatchNum + "%")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)

@batch.route('/BatchInfoDetailCreate', methods=['POST', 'GET'])
def BatchInfoDetailCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return insert(BatchInfoDetail, data)

@batch.route('/BatchInfoDetailUpdate', methods=['POST', 'GET'])
def BatchInfoDetailUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return update(BatchInfoDetail, data)

@batch.route('/BatchInfoDetailDelete', methods=['POST', 'GET'])
def BatchInfoDetailDelete():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        return delete(BatchInfoDetail, data)

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
                oclasss = db_session.query(EletronicBatchDataStore).filter(EletronicBatchDataStore.PUID == PUID,
                                                                           EletronicBatchDataStore.BatchID == BatchID).all()
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
        oc = db_session.query(EletronicBatchDataStore).filter(EletronicBatchDataStore.PUIDName == PUIDName,
                                                              EletronicBatchDataStore.BatchID == BatchID,
                                                              EletronicBatchDataStore.Content == ke).first()
        if oc == None:
            db_session.add(EletronicBatchDataStore(BatchID=BatchID, PUIDName=PUIDName, Content=ke, OperationpValue=val,Operator=current_user.Name))
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

@batch.route('/refractometerRedis', methods=['POST', 'GET'])
def refractometerRedis():
    '''
    Redis实时数据
    :return:
    '''
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            data_dict = {}
            redis_conn = redis.Redis(connection_pool=pool)
            bls = constant.REDIS_retxt
            for key in bls:
                key = key.upper()
                if "IME" in key:
                    key = key[0:-3]+"ime"
                data_dict[key] = redis_conn.hget(constant.REDIS_TABLENAME, "t|" + str(key)).decode('utf-8')
            return json.dumps(data_dict, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "折光仪实时数据查询报错Error：" + str(e), current_user.Name)

@batch.route('/refractometerDataHistory', methods=['POST', 'GET'])
def refractometerDataHistory():
    '''
    折光仪历史数据
    :return:
    '''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                begin = data.get('begin')
                end = data.get('end')
                if begin and end:#[t|ZGY_Temp] AS ZGY_Temp
                    sql = "SELECT  [SampleTime],[t|ZGY_ZGL],[t|ZGY_Temp] FROM [MES].[dbo].[DataHistory] WHERE SampleTime BETWEEN '" + begin + "' AND '" + end +"' order by ID"
                    re = db_session.execute(sql).fetchall()
                    db_session.close()
                    div = {}
                    dic = []
                    diy = []
                    for i in re:
                        t = str(i[0].strftime("%Y-%m-%d %H:%M:%S"))
                        v = i[1]
                        r = i[2]
                        if not v:
                            v = ""
                        if not r:
                            r = ""
                        dic.append([t,v])
                        diy.append([t,r])
                    div["ZGL"] = dic
                    div["Temp"] = diy
                    return json.dumps(div, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/EquipmentManagementManual/ManualShow，说明书信息获取Error：" + str(e), current_user.Name)
@batch.route('/basketExtractConcentrationData')
def basketExtractConcentrationData():
    return render_template('./Qualitymanagement/basketExtractConcentrationData.html')
@batch.route('/stirExtractConcentrationData')
def stirExtractConcentrationData():
    return render_template('./Qualitymanagement/stirExtractConcentrationData.html')

# 批记录查询
@batch.route('/BatchSearch')
def BatchSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                BatchNum = data.get("BatchNum")
                Name = data.get("Name")
                dic = {}
                oclass = db_session.query(BatchInfo).filter(BatchInfo.BatchNum == BatchNum).first()
                if Name == "提取":
                    if oclass.PUIDLineName == "篮式":
                        PUID = "1"
                    elif oclass.PUIDLineName == "搅拌":
                        PUID = "3"
                    eqps = db_session.query(ElectronicBatchTwo.EQPID).distinct().filter(ElectronicBatchTwo.PDUnitRouteID == PUID).order_by(("ID")).all()
                    for i in eqps:
                        db_session.query(BatchType)
                        EQPName = db_session.query(Equipment.EQPName).filter(Equipment.ID == i).first()
                        types = db_session.query(BatchType).filter(BatchType.Descrip.like("%"+oclass.PUIDLineName+"%")).all()
                        for type in types:
                            dic[type+"_"+str(i)] = db_session.query(ElectronicBatchTwo.SampleValue).filter(
                                ElectronicBatchTwo.BatchID == BatchNum, ElectronicBatchTwo.EQPID == int(i), ElectronicBatchTwo.Type == type).first()
                    return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "电子批记录查询报错Error：" + str(e), current_user.Name)
            return json.dumps("电子批记录查询", cls=AlchemyEncoder,
                              ensure_ascii=False)

def changef(args):
    if args != None and args != "":
        return str(round(float(args), 2))
    else:
        return ""
def strchange(args):
    if args != None and args != "":
        return str(args)[10:-10]
    else:
        return ""
def strch(args):
    if args != None and args != "":
        return str(args)[0:-7]
    else:
        return ""
def getmax(args):
    num1 = []
    for x in range(len(args)):
        temp = float(args[x].SampleValue)
        num1.append(temp)
        if x == 0:
            unit = args[x].Unit
    return changef(max(num1)) + unit
def getmin(args):
    num1 = []
    for x in range(len(args)):
        temp = float(args[x].SampleValue)
        num1.append(temp)
        if x == 0:
            unit = args[x].Unit
    return changef(min(num1)) + unit
def searO(BrandName, BatchID, PID, EQPID, Type):
    re = db_session.query(ElectronicBatchTwo).filter(ElectronicBatchTwo.BrandName == BrandName,
                                                     ElectronicBatchTwo.BatchID == BatchID,
                                                     ElectronicBatchTwo.PDUnitRouteID == PID,
                                                     ElectronicBatchTwo.EQPID == EQPID, ElectronicBatchTwo.Type == Type).first()
    if re == None:
        electronicBatch = ElectronicBatchTwo()
        electronicBatch.SampleValue = ""
        electronicBatch.Unit = ""
        electronicBatch.SampleDate = ""
        return electronicBatch
    else:
        return re
def searJZ(BrandName, BatchID, PID, EQPID, Type):
    re = db_session.query(ElectronicBatchTwo).filter(ElectronicBatchTwo.BrandName == BrandName,
                                                     ElectronicBatchTwo.BatchID == BatchID,
                                                     ElectronicBatchTwo.PDUnitRouteID == PID,
                                                     ElectronicBatchTwo.EQPID == EQPID, ElectronicBatchTwo.Type == Type).first()
    if re == None:
        electronicBatch = ElectronicBatchTwo()
        electronicBatch.SampleValue = ""
        electronicBatch.Unit = ""
        electronicBatch.SampleDate = ""
        return electronicBatch
    else:
        return re
def searchEqpID(BrandName, BatchID, PID, name):
    EQPIDs = db_session.query(Equipment.ID).filter(Equipment.PUID == PID,
                                                   Equipment.EQPName.like("%" + name + "%")).all()
    EQPS = db_session.query(ElectronicBatchTwo.EQPID).distinct().filter(ElectronicBatchTwo.PDUnitRouteID == PID,
                                                                        ElectronicBatchTwo.BrandName == BrandName,
                                                                        ElectronicBatchTwo.BatchID == BatchID).all()
    tmp = [val for val in EQPIDs if val in EQPS]
    return tmp