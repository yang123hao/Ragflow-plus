import logging
import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from routes import register_routes

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docker", ".env"))

app = Flask(__name__)
# 启用CORS，允许前端访问
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# 注册所有路由
register_routes(app)

# 从环境变量获取配置
ADMIN_USERNAME = os.getenv("MANAGEMENT_ADMIN_USERNAME", "administrator")
ADMIN_PASSWORD = os.getenv("MANAGEMENT_ADMIN_PASSWORD", "@worklan18")
JWT_SECRET = os.getenv("MANAGEMENT_JWT_SECRET", "your-secret-key")


# 设置日志目录和文件名
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "parser.log")

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),  # 同时也输出到控制台
    ],
)


# 生成token
def generate_token(username):
    # 设置令牌过期时间（1小时后过期）
    current_time = datetime.utcnow()
    expire_time = current_time + timedelta(hours=1)   
    # 生成令牌
    payload = {
        "username": username,
        "exp": expire_time,
        "iat": current_time  # 添加签发时间
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return token


# 登录路由保留在主文件中
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    print("username",username)
    print("password",password)
    # 创建用户名和密码的映射
    valid_users = {ADMIN_USERNAME: ADMIN_PASSWORD}

    # 验证用户名是否存在
    if not username or username not in valid_users:
        return {"code": 1, "message": "用户名不存在"}, 400

    # 验证密码是否正确
    if not password or password != valid_users[username]:
        return {"code": 1, "message": "密码错误"}, 400

    # 生成token
    token = generate_token(username)
    return {"code": 0, "data": {"token": token}, "message": "登录成功"}

# 测试JWT验证的接口
@app.route("/api/v1/auth/test", methods=["GET"])
def test_jwt():
    """测试JWT验证的接口"""
    from utils import jwt_required
    
    @jwt_required
    def protected_function():
        return {"code": 0, "message": "JWT验证成功", "data": {"user": request.user}}
    
    return protected_function()

if __name__ == "__main__":
    # 强制使用5001端口，忽略环境变量
    port = int(os.getenv("FLASK_RUN_PORT", "5001"))
    # 确保端口是5001
    if port != 5001:
        print(f"警告：检测到端口配置为{port}，强制使用5001端口")
        port = 5001
    
    print(f"启动Flask应用，端口：{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
