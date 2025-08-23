import base64
import uuid

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from flask import jsonify
from werkzeug.security import generate_password_hash


# 生成随机的 UUID 作为 id
def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")


# RSA 加密密码
def rsa_psw(password: str) -> str:
    pub_key = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArq9XTUSeYr2+N1h3Afl/z8Dse/2yD0ZGrKwx+EEEcdsBLca9Ynmx3nIB5obmLlSfmskLpBo0UACBmB5rEjBp2Q2f3AG3Hjd4B+gNCG6BDaawuDlgANIhGnaTLrIqWrrcm4EMzJOnAOI1fgzJRsOOUEfaS318Eq9OVO3apEyCCt0lOQK6PuksduOjVxtltDav+guVAA068NrPYmRNabVKRNLJpL8w4D44sfth5RvZ3q9t+6RTArpEtc5sh5ChzvqPOzKGMXW83C95TxmXqpbK6olN4RevSfVjEAgCydH6HN6OhtOQEcnrU97r9H0iZOWwbw3pVrZiUkuRD1R56Wzs2wIDAQAB
    -----END PUBLIC KEY-----"""

    rsa_key = RSA.import_key(pub_key)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted_data = cipher.encrypt(base64.b64encode(password.encode()))
    return base64.b64encode(encrypted_data).decode()


# 加密密码
def encrypt_password(raw_password: str) -> str:
    base64_password = base64.b64encode(raw_password.encode()).decode()
    return generate_password_hash(base64_password)


# 标准响应格式
def success_response(data=None, message="操作成功", code=0):
    return jsonify({"code": code, "message": message, "data": data})


# 错误响应格式
def error_response(message="操作失败", code=500, details=None):
    """标准错误响应格式"""
    response = {"code": code, "message": message}
    if details:
        response["details"] = details
    return jsonify(response), code if code >= 400 else 500

# JWT验证相关函数
import jwt
from functools import wraps
from flask import request, jsonify
import os

# 从环境变量获取JWT密钥
JWT_SECRET = os.getenv("MANAGEMENT_JWT_SECRET", "your-secret-key")

def verify_jwt_token(token):
    """验证JWT token"""
    try:
        # 解码并验证token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token已过期"
    except jwt.InvalidTokenError:
        return False, "无效的Token"
    except Exception as e:
        return False, f"Token验证失败: {str(e)}"

def jwt_required(f):
    """JWT验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return error_response("缺少Authorization头", 401)
        
        # 检查Bearer格式
        if not auth_header.startswith('Bearer '):
            return error_response("Authorization头格式错误", 401)
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        is_valid, payload = verify_jwt_token(token)
        
        if not is_valid:
            return error_response(payload, 401)
        
        # 将用户信息添加到请求上下文
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function
