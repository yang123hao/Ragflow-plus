#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速调试脚本 - 用于简单测试conversation service
"""

import sys
import os

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, server_dir)

def quick_test():
    """快速测试函数"""
    try:
        # 测试导入
        print("正在导入模块...")
        from services.conversation.service import get_conversations_by_user_id
        
        print("✓ 模块导入成功!")
        
        # 测试函数调用
        print("正在测试函数调用...")
        user_id = "test_user"
        result = get_conversations_by_user_id(user_id, 1, 5)
        
        print(f"✓ 函数调用成功! 返回结果: {len(result[0])} 个对话")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
