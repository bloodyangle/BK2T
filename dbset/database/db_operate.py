import json
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from flask_login import current_user
import pymssql

GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:root@localhost:1433/BK?charset=utf8"
engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()


