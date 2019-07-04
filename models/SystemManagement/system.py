from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine,ForeignKey, Table,Column, DateTime, Integer, String, Unicode
from sqlalchemy.dialects.mssql.base import BIT
from werkzeug.security import generate_password_hash, check_password_hash
from dbset.database.db_operate import GLOBAL_DATABASE_CONNECT_STRING
from datetime import datetime
from flask_login import LoginManager

login_manager = LoginManager()
# 创建对象的基类
engine = create_engine(GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session= Session()
Base = declarative_base(engine)

# 菜单与角色关联表
Role_Menu = Table(
    "role_menu",
    Base.metadata,
    Column("Role_ID", Integer, ForeignKey("role.ID"), nullable=False, primary_key=True),
    Column("Menu_ID", Integer, ForeignKey("menu.ID"), nullable=False, primary_key=True)
)

class SysLog(Base):
	__tablename__ = "SysLog"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

	# IP:
	IP = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 计算机名称:
	ComputerName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 操作用户:
	UserName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 操作日期:
	OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

	# 操作内容:
	OperationContent = Column(Unicode(2048), primary_key=False, autoincrement=False, nullable=True)

	# 类型:
	OperationType = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

# 模块菜单表
class Menu(Base):
    __tablename__ = 'menu'
    # 模块ID
    ID = Column(Integer, primary_key=True, autoincrement=True)

    # 模块名称
    ModuleName = Column(Unicode(32), nullable=False)

    # 模块编码
    ModuleCode = Column(String(100),nullable=False)

    # 模块路由
    Url = Column(String(100), nullable=True)

    # 描述
    Description = Column(Unicode(1024), nullable=True)

    # 创建时间
    CreateDate = Column(DateTime, default=datetime.now, nullable=True)

    # 创建人
    Creator = Column(Unicode(50), nullable=True)

    # 父节点
    ParentNode = Column(Integer, nullable=True)

    # 查询角色
    roles = relationship("Role", secondary=Role_Menu)

# 角色表
class Role(Base):
    __tablename__ = 'role'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # # 角色编码:
    # RoleCode = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

    # 角色顺序:
    RoleSeq = Column(String(10), primary_key=False, autoincrement=False, nullable=True)

    # 角色名称:
    RoleName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 角色说明:
    Description = Column(Unicode(62), primary_key=False, autoincrement=False, nullable=True)

    # 创建人:
    CreatePerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间:
    CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 父节点
    ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 查询权限
    menus = relationship("Menu", secondary=Role_Menu)

# 用户表
class User(Base):
    __tablename__ = 'user'

    # id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户名
    Name = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 密码
    Password = Column(String(128), nullable=False)

    # 工号
    WorkNumber = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    #登录状态
    Status = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    #创建用户
    Creater = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    #创建时间
    CreateTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    #上次登录时间
    LastLoginTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    #是否锁定
    IsLock = Column(BIT, primary_key=False, autoincrement=False, nullable=True)

    #所属部门
    OrganizationName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 角色名称:
    RoleName = Column(Unicode(128), primary_key=False, autoincrement=False, nullable=True)

    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute')

    # 定义password字段的写方法，我们调用generate_password_hash将明文密码password转成密文Shadow
    # @password.setter
    def password(self, password):
        self.Password = generate_password_hash(password)
        return self.Password

    # 定义验证密码的函数confirm_password
    def confirm_password(self, password):
        return check_password_hash(self.Password, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # python 3

# Organization:
class Organization(Base):
    __tablename__ = "Organization"

    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 组织结构编码:
    OrganizationCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 父组织机构:
    ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 顺序号:
    OrganizationSeq = Column(Unicode(10), primary_key=False, autoincrement=False, nullable=True)

    # 组织机构名称:
    OrganizationName = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 说明:
    Description = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 创建人:
    CreatePerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间:
    CreateDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 显示图标:
    Img = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True, default="antonio.jpg")

    # 显示图标:
    Color = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True,  default="#1696d3")

# Equipment:
class Equipment(Base):
    __tablename__ = "Equipment"

    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

    # 设备编码:
    EQPCode = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

    # 设备名称:
    EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # OpcTag:
    BatchOpcTag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # OpcTag:
    BrandOpcTag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 供应商:
    SupplierName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 设备状态:
    Equipment_State = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 基本参数:
    Equipment_Model = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 成本归属:
    CostAttach = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 采购日期:
    Procurement_Date = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, primary_key=False, nullable=True)

    # 备注说明:
    Desc = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

# 电子批记录
class ElectronicBatch(Base):
    __tablename__ = 'ElectronicBatch'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # id:
    TaskID = Column(Integer, primary_key=False, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段编码:
    PDUnitRouteID = Column(Integer, nullable=False, primary_key=False)

    # 设备编码
    EQPID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    OpcTagID = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 采样值:
    SampleValue = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 采样时间:
    SampleDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 重复次数：
    RepeatCount = Column(Integer, primary_key=False, autoincrement=False, nullable=True, default=0)

    # 描述:
    Description = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Type = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 单位:
    Unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 电子批记录
class ElectronicBatchTwo(Base):
    __tablename__ = 'ElectronicBatchTwo'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # id:
    TaskID = Column(Integer, primary_key=False, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段编码:
    PDUnitRouteID = Column(Integer, nullable=False, primary_key=False)

    # 设备编码
    EQPID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    OpcTagID = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 采样值:
    SampleValue = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 采样时间:
    SampleDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 重复次数：
    RepeatCount = Column(Integer, primary_key=False, autoincrement=False, nullable=True, default=0)

    # 描述:
    Description = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Type = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 单位:
    Unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 审计追踪
class AuditTrace(Base):
    __tablename__ = 'AuditTrace'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 操作:
    Operation = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 详细信息:
    DeitalMSG = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 修改日期
    ReviseDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 用户:
    User = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 其他:
    Other = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

class QualityControlTree(Base):
	__tablename__ = "QualityControlTree"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# 生产线
	Name = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 工序
	Note = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True	)

	# 设备号
	EquipmentCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 批次
	BatchTag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 品名W
	Brand = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 父节点
	ParentNode = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

# 批次表
class BatchInfo(Base):
    __tablename__ = "BatchInfo"

    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号
    BatchNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 品名
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 药材规格
    MedicinalType = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 工艺生产线
    PUIDLineName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间
    CreateDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 修改时间
    UpdateDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 批次维护表
class BatchInfoDetail(Base):
    __tablename__ = "BatchInfoDetail"

    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号
    BatchNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 品名
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 设备ID
    EQPID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 品名ID
    BrandID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段
    PUIDName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID
    PUID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 开始时间
    StartDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 结束时间
    EndDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 修改时间
    UpdateDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 批记录操作步骤（SOP）
class EletronicBatchDataStore(Base):
    __tablename__ = 'EletronicBatchDataStore'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作步骤内容:
    Content = Column(String(60), primary_key=False, autoincrement=False, nullable=True)

    # 操作值:
    OperationpValue = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    #操作人:
    Operator = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)

    # 描述:
    Description = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

# 批记录TYPE
class BatchType(Base):
    __tablename__ = 'BatchType'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批记录类型:
    Type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 批记录类型说明:
    Descrip = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

# 品名维护表
class BrandFlag(Base):
    __tablename__ = 'BrandFlag'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 品名:
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 品名标识:
    BrandNameFlag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 流程确认表
class FlowConfirm(Base):
    __tablename__ = 'FlowConfirm'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次:
    BatchNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 确认流程:
    ConfirmFlow = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 确认人:
    Confirmer = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 确认时间:
    ConfirmTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 修改时间:
    UpdateTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # key:
    key = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)


# 生成表单的执行语句
Base.metadata.create_all(engine)

