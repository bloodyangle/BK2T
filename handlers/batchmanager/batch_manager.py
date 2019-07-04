import redis
from flask import Blueprint, render_template, request, make_response
import json
import datetime
from sqlalchemy import desc

from dbset.database.db_operate import db_session,pool
from dbset.main.BSFramwork import AlchemyEncoder
from models.SystemManagement.system import BatchInfoDetail, EletronicBatchDataStore, Equipment, BatchType, \
    ElectronicBatchTwo, BatchInfo, AuditTrace
from dbset.log.BK2TLogger import logger,insertSyslog
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
from tools.common import insert,delete,update
from dbset.database import constant

batch = Blueprint('batch', __name__, template_folder='templates')

@batch.route('/ElectronicBatchRecordNav')
def electronicBatchRecord():
    return render_template('./ProductionManagement/electronicBatchRecordNav.html')
@batch.route('/ElectronicBatchRecord', methods=['POST', 'GET'])
def ElectronicBatchRecord():
    if request.method == 'GET':
        data = request.values
        BatchNum = data.get('BatchID')
        title = data.get('title')
        if title == "提取":
            PUIDLineName = db_session.query(BatchInfo.PUIDLineName).filter(BatchInfo.BatchNum == BatchNum).first()
            title = PUIDLineName[0] + data.get('title')
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
                begin = data.get('begin')
                end = data.get('end')
                BatchNum = data.get('BatchNum')
                if(BatchNum == "" or BatchNum == None):
                    total = db_session.query(BatchInfo).filter(BatchInfo.CreateDate.between(begin, end)).order_by(desc("CreateDate")).count()
                    oclass = db_session.query(BatchInfo).filter(BatchInfo.CreateDate.between(begin, end)).order_by(desc("CreateDate")).all()[inipage:endpage]
                else:
                    total = db_session.query(BatchInfo).filter(BatchInfo.BatchNum.like("%" + BatchNum + "%"), BatchInfo.CreateDate.between(begin, end)).order_by(desc("CreateDate")).count()
                    oclass = db_session.query(BatchInfo).filter(BatchInfo.BatchNum.like("%" + BatchNum + "%"), BatchInfo.CreateDate.between(begin, end)).order_by(desc("CreateDate")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/BatchInfoSearch查询报错Error：" + str(e), current_user.Name)

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
                BatchNum = data.get('BatchNum')
                total = db_session.query(BatchInfoDetail).filter(BatchInfoDetail.BatchNum == BatchNum).count()
                oclass = db_session.query(BatchInfoDetail).filter(BatchInfoDetail.BatchNum == BatchNum).all()[inipage:endpage]
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
                if key == "Name":
                    continue
                if key == "BatchID":
                    continue
                val = data.get(key)
                addUpdateEletronicBatchDataStore(data.get("Name"), data.get("BatchID"), key, val)
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
                PUID = data['Name']
                BatchID = data['BatchID']
                oclasss = db_session.query(EletronicBatchDataStore).filter(EletronicBatchDataStore.BatchID == BatchID, EletronicBatchDataStore.PUID == PUID).all()
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
def addUpdateEletronicBatchDataStore(PUID, BatchID, ke, val):
    try:
        oc = db_session.query(EletronicBatchDataStore).filter(EletronicBatchDataStore.PUID == PUID,
                                                              EletronicBatchDataStore.BatchID == BatchID,
                                                              EletronicBatchDataStore.Content == ke).first()
        if oc == None:
            db_session.add(EletronicBatchDataStore(BatchID=BatchID, PUID=PUID, Content=ke, OperationpValue=val,Operator=current_user.Name))
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
@batch.route('/OperatorCheckSaveUpdate', methods=['POST', 'GET'])
def OperatorCheckSaveUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            PUID = data.get("Name")
            BatchID = data.get("BatchID")
            for key in data.keys():
                if key == "Name":
                    continue
                if key == "BatchID":
                    continue
                val = data.get(key)
                oc = db_session.query(EletronicBatchDataStore).filter(EletronicBatchDataStore.PUID == PUID,
                                                                      EletronicBatchDataStore.BatchID == BatchID,
                                                                      EletronicBatchDataStore.Content == key).first()
                if oc == None:
                    db_session.add(EletronicBatchDataStore(BatchID=BatchID, PUID=PUID, Content=key, OperationpValue=val,Operator=current_user.Name))
                    db_session.add(AuditTrace(Operation="确认成功", DeitalMSG="用户:"+current_user.Name+" 节点：操作确认", ReviseDate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), User=current_user.Name))
                else:
                    oc.Content = key
                    oc.OperationpValue = val
                    oc.Operator = current_user.Name
                    db_session.add(AuditTrace(Operation="确认成功", DeitalMSG="用户:" + current_user.Name + " 节点：操作确认",
                                              ReviseDate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                              User=current_user.Name))
                db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "/OperatorCheckSaveUpdate报错：" + str(e), current_user.Name)
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

@batch.route('/DataHistorySelect', methods=['POST', 'GET'])
def DataHistorySelect():
    '''
    历史数据曲线
    '''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                begin = data.get('begin')
                end = data.get('end')
                variable = data.get('variable')
                Name = data.get('Name')
                if begin and end:
                    div = {}
                    dic = []
                    dir = []
                    die = []
                    if Name == "提取":
                        sql = "SELECT  [SampleTime]," + format(variable) + " FROM [BK].[dbo].[DataHistory] WHERE SampleTime BETWEEN '" + format(begin) + "' AND '" + format(end) + "' order by ID"
                        re = db_session.execute(sql).fetchall()
                        db_session.close()
                        for i in re:
                            t = str(i[0].strftime("%Y-%m-%d %H:%M:%S"))
                            v = i[1]
                            if not v:
                                v = ""
                            r = i[2]
                            if not r:
                                r = ""
                            dir.append([t, r])
                            dic.append([t, v])
                        div["WD"] = dic
                        div["YL"] = dir
                    elif Name == "浓缩":
                        sql = "SELECT  [SampleTime]," + format(variable) + " FROM [BK].[dbo].[DataHistory] WHERE SampleTime BETWEEN '" + format(begin) + "' AND '" + format(end) + "' order by ID"
                        re = db_session.execute(sql).fetchall()
                        db_session.close()
                        for i in re:
                            t = str(i[0].strftime("%Y-%m-%d %H:%M:%S"))
                            v = i[1]
                            if not v:
                                v = ""
                            r = i[2]
                            if not r:
                                r = ""
                            e = i[3]
                            if not e:
                                e = ""
                            dic.append([t, v])
                            dir.append([t, r])
                            die.append([t, e])
                        div["YL"] = dic
                        div["MD"] = dir
                        div["WD"] = die
                    return json.dumps(div, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/DataHistorySelect，历史数据曲线获取Error：" + str(e), current_user.Name)
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
                    eqps = db_session.query(ElectronicBatchTwo.EQPID).distinct().filter(ElectronicBatchTwo.BatchID == BatchNum, ElectronicBatchTwo.PDUnitRouteID == PUID).order_by(("EQPID")).all()
                    j = 1
                    for i in eqps:
                        EQPName = db_session.query(Equipment.EQPName).filter(Equipment.ID == i[0]).first()
                        btss = db_session.query(BatchType).filter(BatchType.Descrip.like("%"+oclass.PUIDLineName+"%")).all()
                        for bt in btss:
                            type = bt.Type
                            if type == "_Batch_LS_Action01" or type == "_Batch_JB_Action01":
                                dic[type + "_" + str(j)] = EQPName[0]
                            else:
                                ret = queryvalue(BatchNum, int(i[0]), bt.Descrip)
                                dic[type+"_"+str(j)+"_1"] = ret[0]
                                dic[type + "_" + str(j) + "_2"] = ret[1]
                        j = j + 1
                    dic["BatchNum"] = oclass.BatchNum
                    dic["MedicinalType"] = oclass.MedicinalType
                    dic["BrandName"] = oclass.BrandName
                    return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "电子批记录查询报错Error：" + str(e), current_user.Name)
            return json.dumps("电子批记录查询", cls=AlchemyEncoder,
                              ensure_ascii=False)
def queryvalue(BatchNum, EQPID, type):
    SampleValues = db_session.query(ElectronicBatchTwo.SampleValue).filter(
                                        ElectronicBatchTwo.BatchID == BatchNum, ElectronicBatchTwo.EQPID == EQPID, ElectronicBatchTwo.Type == type).order_by(("SampleDate")).all()
    dir = []
    if len(SampleValues) == 1:
        SampleValue1 = SampleValues[0][0]
        if len(SampleValue1) > 18:
            dir.append(strch(SampleValue1))
        else:
            dir.append(SampleValue1)
        dir.append("")
    elif len(SampleValues) == 2:
        SampleValue1 = SampleValues[0][0]
        if SampleValue1 == None or SampleValue1 == "":
            dir.append("")
        else:
            if len(SampleValue1) > 18:
                dir.append(strch(SampleValue1))
            else:
                dir.append(SampleValue1)
        SampleValue2 = SampleValues[1][0]
        if SampleValue1 == None or SampleValue1 == "":
            dir.append("")
        else:
            if len(SampleValue2) > 18:
                dir.append(strch(SampleValue2))
            else:
                dir.append(SampleValue2)
    elif SampleValues == None or len(SampleValues) < 1 or len(SampleValues) > 2:
        dir.append("")
        dir.append("")
    return dir
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
def searchEqpID(BrandName, BatchID, PID, name):
    EQPIDs = db_session.query(Equipment.ID).filter(Equipment.PUID == PID,
                                                   Equipment.EQPName.like("%" + name + "%")).all()
    EQPS = db_session.query(ElectronicBatchTwo.EQPID).distinct().filter(ElectronicBatchTwo.PDUnitRouteID == PID,
                                                                        ElectronicBatchTwo.BrandName == BrandName,
                                                                        ElectronicBatchTwo.BatchID == BatchID).all()
    tmp = [val for val in EQPIDs if val in EQPS]
    return tmp
@batch.route('/BatchUpdate', methods=['POST', 'GET'])
def BatchUpdate():
    if request.method == 'POST':
        try:
            data = request.values
            BatchID = data.get("BatchNum")
            EQPName = data.get("EQPName")
            SampleValue = data.get("SampleValue")
            EQPID = db_session.query(Equipment.ID).filter(Equipment.EQPName == EQPName).first()[0]
            Type = data.get("Type")
            Type = Type[0:-5]
            oclass = db_session.query(ElectronicBatchTwo).filter(ElectronicBatchTwo.BatchID == BatchID,ElectronicBatchTwo.Type == Type,ElectronicBatchTwo.EQPID == EQPID).first()
            oclass.SampleValue = SampleValue
            db_session.commit()
            return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "电子批记录修改报错Error：" + str(e), current_user.Name)
            return json.dumps("电子批记录修改", cls=AlchemyEncoder,ensure_ascii=False)

