from flask import Flask, render_template
from flask_login import login_required
from dbset.account import auth_lib
from handlers.account import account_auth
from handlers.SystemManagement import user_management, PermissionAssignment,Role_management
from handlers.QualityManagement import ProcessContinuousData
from handlers.main import home
from handlers.SystemManagement.organization_model import organiza
from handlers.EquipmentModel.euipment_model import equip
from handlers.ProductionManagement.producebatch_model import produce
from handlers.SystemManagement.systemlog import systemlog
from flask_bootstrap import Bootstrap
from handlers.batchmanager.batch_manager import batch

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'qeqhdasdqiqd131'
account_auth.login_manager.init_app(app)

# 将后台函数传到前端
app.add_template_global(auth_lib.isIn, 'isIn')

# 登录
app.register_blueprint(account_auth.login_auth)
# 用户管理
app.register_blueprint(user_management.user_manage)
# 角色管理
app.register_blueprint(Role_management.role_management)
# 主页
app.register_blueprint(home.home_page)
# 权限分配
app.register_blueprint(PermissionAssignment.permission_distribution)
#组织机构
app.register_blueprint(organiza)
#设备管理
app.register_blueprint(equip)
#生产数据管理
app.register_blueprint(produce)
# 过程连续数据
# app.register_blueprint(ProcessContinuousData.continuous_data)
# 日志模块
app.register_blueprint(systemlog)
# 批次管理
app.register_blueprint(batch)

@app.route('/')
@login_required
def hello_world():
    return render_template("./main/main.html")

if __name__ == "__main__":
    app.run(debug=True)
