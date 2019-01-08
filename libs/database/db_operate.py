#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:mr_mao_murray
@file: test.py
@time: 2018/12/17
"""
# import redis
# from constant import constant
# def func(li):
#     pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)  # 实现一个连接池
#     redis_conn = redis.Redis(connection_pool=pool)
#     for arg in li:
#         data = redis_conn.hget(constant.REDIS_TABLENAME, "t|" + arg)
#         print(arg,":", data.decode('utf-8'))
#
# chunchen = ["设备3_3#自动命令_自动输出","名称_nam3","名称_batch3","模拟量_进醇沉物料流量计","过程值_3#浸膏累计值","过程值_3#酒精累计值"]
# single = ['名称_nam5','名称_batch5','模拟量_浓缩蒸汽压力计','模拟量_浓缩分离室真空计','模拟量_浓缩分离室温度计','模拟量_浓缩药液密度计']
# # func(single)
# mvr_1 = ['MVRPM_1','MVRPC_1','KWH_1','JL_SUM_1','WATER_SUM_1']
# mvr_2 = ['MVRPM_2','MVRPC_2','KWH_2','JL_SUM_2','WATER_SUM_2']
# mvr_3 = ['MVRPM_3','MVRPC_3','KWH_3','JL_SUM_3','WATER_SUM_3']
# func(mvr_3)

from Model.Global import GLOBAL_DATABASE_CONNECT_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Model.system import Organization
from MES import logger, insertSyslog, current_user
import json
import Model

engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()


def insert(tablename, insert_dict):
    if tablename.__tablename__:
        oclass = tablename()
        if isinstance(insert_dict, dict):
            try:
                for key in insert_dict.keys():
                    oclass.key = insert_dict[key]
                db_session.add(oclass)
                db_session.commit()
            except Exception as e:
                logger.error(e)
                insertSyslog("error", "%s数据添加报错Error："%tablename + str(e), current_user.Name)
                return json.dumps("%s数据添加报错Error"%tablename, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

def delete(tablename, recv_data):
    if tablename.__tablename__:
        if isinstance(recv_data, list):
            try:
                for id in recv_data:
                    Table_ID = int(id)
                    oclass = db_session.query(tablename).filter(tablename.ID == Table_ID).first()
                    if oclass:
                        db_session.delete(oclass)
                        db_session.commit()
                    return {"status":''}
            except Exception as e:
                logger.error(e)
                insertSyslog("error", "%s数据删除报错Error："%tablename + str(e), current_user.Name)
                return json.dumps("%s数据删除报错Error"%tablename, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

def update(tablename, recv_data):
    pass