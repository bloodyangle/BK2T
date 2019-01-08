import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libs.log.BK2TLogger import logger
from libs.log.BK2TLogger import insertSyslog
from libs.main.BSFramwork import AlchemyEncoder



GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:Qcsw@758@192.168.2.121:1433/MES?charset=utf8"
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
                return json.dumps("%s数据添加报错Error"%tablename, cls=AlchemyEncoder, ensure_ascii=False)

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
                return json.dumps("%s数据删除报错Error"%tablename, cls=AlchemyEncoder, ensure_ascii=False)

def update(tablename, recv_data):
    pass