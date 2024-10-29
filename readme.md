# 宠物美容预约系统后端 API

## 项目介绍
这是一个基于 Django REST Framework 开发的宠物美容预约系统后端 API。系统提供完整的预约管理、客户管理、宠物管理和服务管理功能。

## 技术栈
- Python 3.11+
- Django 5.0
- Django REST Framework
- SQLite3 (可迁移至其他数据库)
- JWT认证
- Swagger/ReDoc API文档

## 主要功能

### 1. 客户管理 (accounts)
- 用户注册/登录
- JWT身份验证
- 用户信息管理
- 头像上传

### 2. 宠物管理 (pets)
- 宠物信息维护
- 宠物体型自动计算
- 宠物健康记录
- 宠物照片管理

### 3. 服务管理 (services)
- 服务项目管理
- 基于宠物体型的差异化定价
- 服务时长管理
- 服务状态控制

### 4. 预约管理 (appointments)
- 在线预约服务
- 自动计算服务价格
- 预约状态管理(待确认/已确认/已完成/已取消)
- 预约时间冲突检测
- 工作人员备注功能

### 5. 营业时间管理 (business_hours)
- 每周营业时间设置
- 营业状态管理
- 可用时间段计算

### 6. 假期管理 (holidays)
- 节假日设置
- 特殊休息日管理

## 项目设置

### 环境要求
```plaintext
Python 3.11 或更高版本
pip 包管理工具
```

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd pet-grooming-backend
```

2. 创建虚拟环境
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

6. 创建超级用户
```bash
python manage.py createsuperuser
```

7. 运行开发服务器
```bash
python manage.py runserver
```

## API 文档

启动服务器后，可以通过以下地址访问API文档：
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API 端点概览

### 认证相关
- POST /api/auth/register/ - 用户注册
- POST /api/auth/login/ - 用户登录
- POST /api/auth/token/refresh/ - 刷新访问令牌

### 宠物管理
- GET /api/pets/ - 获取宠物列表
- POST /api/pets/ - 创建新宠物
- GET /api/pets/{id}/ - 获取宠物详情
- PUT /api/pets/{id}/ - 更新宠物信息
- DELETE /api/pets/{id}/ - 删除宠物

### 服务管理
- GET /api/services/ - 获取服务列表
- GET /api/services/{id}/ - 获取服务详情
- GET /api/services/{id}/prices/ - 获取服务价格

### 预约管理
- GET /api/appointments/ - 获取预约列表
- POST /api/appointments/ - 创建新预约
- GET /api/appointments/{id}/ - 获取预约详情
- POST /api/appointments/{id}/cancel/ - 取消预约
- POST /api/appointments/{id}/confirm/ - 确认预约
- GET /api/appointments/available-slots/ - 获取可用时间段

### 营业时间和假期
- GET /api/business-hours/ - 获取营业时间
- GET /api/holidays/ - 获取假期列表

## 开发规范

### 代码风格
- 遵循 PEP 8 编码规范
- 使用 4 空格缩进
- 使用清晰的命名约定

### API 设计原则
- 遵循 RESTful API 设计原则
- 使用合适的 HTTP 方法和状态码
- 提供清晰的错误信息

### 安全性
- 使用 JWT 进行身份验证
- 实施适当的权限控制
- 数据验证和清理

## 部署说明

### 生产环境配置
1. 设置 DEBUG=False
2. 配置安全的 SECRET_KEY
3. 配置允许的主机
4. 配置数据库
5. 配置静态文件服务
6. 配置媒体文件存储

### 数据库迁移
```bash
python manage.py migrate
```

### 静态文件收集
```bash
python manage.py collectstatic
```

## 维护和支持

### 日志管理
- 应用程序日志位于 logs/ 目录
- 使用不同的日志级别进行错误跟踪

### 备份
- 定期备份数据库
- 备份媒体文件
