from flask import Blueprint, render_template, request, make_response
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from libs.database.db_operate import GLOBAL_DATABASE_CONNECT_STRING


engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

organiza = Blueprint('organiza', __name__)

# 组织机构建模
@organiza.route('/organization')
def organization():
    return render_template('sysOrganization.html')
