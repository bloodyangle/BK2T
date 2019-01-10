import json
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from libs.log.BK2TLogger import logger
from libs.log.BK2TLogger import insertSyslog
from libs.main.BSFramwork import AlchemyEncoder
from flask_login import current_user


GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:Qcsw@758@192.168.2.121:1433/BK2T?charset=utf8"
engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()




def insert(tablename, insert_dict):
    '''
    :param tablename: 要进行插入数据的model
    :param insert_dict: 要进行插入的数据，数据类型为dict，key为model的字段属性，value为要插入的值
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        oclass = tablename()
        if isinstance(insert_dict, dict) and len(insert_dict) > 0:
            try:
                for key in insert_dict.keys():
                    setattr(oclass, key, insert_dict[key])
                db_session.add(oclass)
                db_session.commit()
                return json.dumps({'status':'OK', 'message': '数据添加成功！'}, cls=AlchemyEncoder, ensure_ascii=False)
            except Exception as e:
                logger.error(e)
                insertSyslog("error", "%s数据添加报错："%tablename + str(e), current_user.Name)
                return json.dumps({'status':'error', 'message': '数据添加失败！'}, cls=AlchemyEncoder, ensure_ascii=False)
        else:
            return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
    else:
        return json.dumps({'status':'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)

def delete(tablename, recv_data):
    '''
    :param tablename: 要进行删除信息的model
    :param recv_data: 要进行更新的数据，数据类型为list，list中的每个元素为需要删除的每条记录的ID
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        if isinstance(recv_data, list) and len(recv_data) > 0:
            try:
                for id in recv_data:
                    Table_ID = int(id)
                    oclass = db_session.query(tablename).filter(tablename.ID == Table_ID).first()
                    if oclass:
                        db_session.delete(oclass)
                        db_session.commit()
                return json.dumps({'status': 'OK', 'message': '数据删除成功！'}, cls=AlchemyEncoder, ensure_ascii=False)
            except Exception as e:
                logger.error(e)
                insertSyslog("error", "%s数据删除报错："%tablename + str(e), current_user.Name)
                return json.dumps({'status':'error', 'message': '数据删除失败！'}, cls=AlchemyEncoder, ensure_ascii=False)
        else:
            return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)

def update(tablename, new_data):
    '''
    :param tablename:要进行更新的model
    :param new_data: 要进行更新的数据，数据类型为dict，key为model的字段属性，value为要更新的值
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        if isinstance(new_data, dict) and len(new_data) > 0:
            try:
                oclass = db_session.query(tablename).filter(tablename.ID==new_data['ID']).first()
                if oclass:
                    for key in new_data.keys():
                        if hasattr(oclass, key):
                            setattr(oclass, key, new_data[key])
                        else:
                            json.dumps({'status': 'error', 'message': '数据更新失败！'}, cls=AlchemyEncoder,ensure_ascii=False)
                    db_session.add(oclass)
                    db_session.commit()
                    return json.dumps({'status': 'OK', 'message': '数据更新成功！'}, cls=AlchemyEncoder, ensure_ascii=False)
                else:
                    return json.dumps({'status': 'error', 'message': '当前记录不存在！'}, cls=AlchemyEncoder, ensure_ascii=False)
            except Exception as e:
                logger.error(e)
                insertSyslog("error", "%s数据更新报错："%tablename + str(e), current_user.Name)
                return json.dumps({'status':'error', 'message': '数据更新失败！'}, cls=AlchemyEncoder, ensure_ascii=False)
        else:
            return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)

def FuzzyQuery(tablename, params):
    '''
    :param tablename: 要进行查询的model
    :param params: 一个字典，字典中的key为model的字段，value为进行查询的关键字
    :return: 返回json信息，包含status，message，data
    '''
    if hasattr(tablename, '__tablename__'):
        if isinstance(params, dict) and len(params) > 0:
            for key in params.keys():
                if hasattr(tablename, key):
                    try:
                        data = db_session.query(tablename).filter(tablename.key.like(params[key])).all()
                        if data:
                            return json.dumps({'status': 'OK', 'message': '数据更新成功！', 'data':data}, cls=AlchemyEncoder, ensure_ascii=False)
                        else:
                            return json.dumps({'status': 'OK', 'message': '未查询到相关的数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
                    except Exception as e:
                        logger.error(e)
                        insertSyslog("error", "%s数据更新报错："%tablename + str(e), current_user.Name)
                return json.dumps({'status':'error', 'message': '数据查询失败，请输入正确的关键字...'}, cls=AlchemyEncoder, ensure_ascii=False)

        else:
            return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)

def ExactQuery(tablename, field, param,type='one'):
    '''
    :param tablename: 需要精确查询的model
    :param field: 查询条件（model的字段）
    :param param: 查询条件的value
    :param type: 查询类型（查询单条type为'one',查询多条为'more'）
    :return: 返回json信息，包含status，message，data
    '''
    if hasattr(tablename, '__tablename__') and hasattr(tablename, field):
        if isinstance(param, str) and len(param) > 0:
            if type == 'one':
                try:
                    one_data = db_session.query(tablename).filter_by(field=param).first()
                    if one_data:
                        return json.dumps({'status': 'OK', 'message': '数据查询成功！', 'data':one_data}, cls=AlchemyEncoder, ensure_ascii=False)
                    else:
                        return json.dumps({'status': 'OK', 'message': '未查询到相关数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
                except Exception as e:
                    logger.error(e)
                    insertSyslog("error", "%s数据更新报错：" % tablename + str(e), current_user.Name)
            if type == 'more':
                try:
                    more_data = db_session.query(tablename).filter_by(field=param).all()
                    if more_data:
                        return json.dumps({'status': 'OK', 'message': '数据查询成功！', 'data':more_data}, cls=AlchemyEncoder, ensure_ascii=False)
                    else:
                        return json.dumps({'status': 'OK', 'message': '未查询到相关数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
                except Exception as e:
                    logger.error(e)
                    insertSyslog("error", "%s数据更新报错：" % tablename + str(e), current_user.Name)
            else:
                return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
        return json.dumps({'status': 'error', 'message': '数据查询失败，请输入正确的关键字...'}, cls=AlchemyEncoder, ensure_ascii=False)
    else:
        return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
