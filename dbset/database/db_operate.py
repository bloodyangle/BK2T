import json
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from flask_login import current_user
import pymssql

GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:root@localhost:1433/BK?charset=utf8"
engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

# def FuzzyQuery(tablename, params):
#     '''
#     :param tablename: 要进行查询的model
#     :param params: 一个字典，字典中的key为model的字段，value为进行查询的关键字
#     :return: 返回json信息，包含status，message，data
#     '''
#     if hasattr(tablename, '__tablename__'):
#         if isinstance(params, dict) and len(params) > 0:
#             for key in params.keys():
#                 if hasattr(tablename, key):
#                     try:
#                         data = db_session.query(tablename).filter_by(key = params[key]).all()
#                         if data:
#                             return json.dumps({'status': 'OK', 'message': '数据更新成功！', 'data':data}, cls=AlchemyEncoder, ensure_ascii=False)
#                         else:
#                             return json.dumps({'status': 'OK', 'message': '未查询到相关的数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
#                     except Exception as e:
#                         logger.error(e)
#                         insertSyslog("error", "%s数据更新报错："%tablename + str(e), current_user.Name)
#                 return json.dumps({'status':'error', 'message': '数据查询失败，请输入正确的关键字...'}, cls=AlchemyEncoder, ensure_ascii=False)
#
#         else:
#             return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
#     else:
#         return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
#
# def ExactQuery(tablename, field, param,type='one'):
#     '''
#     :param tablename: 需要精确查询的model
#     :param field: 查询条件（model的字段）
#     :param param: 查询条件的value
#     :param type: 查询类型（查询单条type为'one',查询多条为'more'）
#     :return: 返回json信息，包含status，message，data
#     '''
#     if hasattr(tablename, '__tablename__') and hasattr(tablename, field):
#         if isinstance(param, str) and len(param) > 0:
#             if type == 'one':
#                 try:
#                     one_data = db_session.query(tablename).filter_by(field=param).first()
#                     if one_data:
#                         return json.dumps({'status': 'OK', 'message': '数据查询成功！', 'data':one_data}, cls=AlchemyEncoder, ensure_ascii=False)
#                     else:
#                         return json.dumps({'status': 'OK', 'message': '未查询到相关数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
#                 except Exception as e:
#                     logger.error(e)
#                     insertSyslog("error", "%s数据更新报错：" % tablename + str(e), current_user.Name)
#             if type == 'more':
#                 try:
#                     more_data = db_session.query(tablename).filter_by(field=param).all()
#                     if more_data:
#                         return json.dumps({'status': 'OK', 'message': '数据查询成功！', 'data':more_data}, cls=AlchemyEncoder, ensure_ascii=False)
#                     else:
#                         return json.dumps({'status': 'OK', 'message': '未查询到相关数据！'}, cls=AlchemyEncoder, ensure_ascii=False)
#                 except Exception as e:
#                     logger.error(e)
#                     insertSyslog("error", "%s数据更新报错：" % tablename + str(e), current_user.Name)
#             else:
#                 return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
#         return json.dumps({'status': 'error', 'message': '数据查询失败，请输入正确的关键字...'}, cls=AlchemyEncoder, ensure_ascii=False)
#     else:
#         return json.dumps({'status': 'error', 'message': '系统错误，请联系系统管理员解决...'}, cls=AlchemyEncoder, ensure_ascii=False)
