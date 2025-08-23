#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本 - 用于测试conversation service
使用方法：
1. 激活虚拟环境：source ../../venv/bin/activate
2. 运行调试：python debug_service.py
3. 或者使用pdb：python -m pdb debug_service.py
"""

import sys
import os
import pdb

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# 添加server目录到路径
server_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, server_dir)

print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}...")

try:
    # 导入需要调试的模块
    from services.conversation.service import get_conversations_by_user_id, get_messages_by_conversation_id
    print("✓ 成功导入conversation service模块")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请确保已激活虚拟环境并安装了所需依赖")
    sys.exit(1)

def test_get_conversations():
    """测试获取对话列表功能"""
    print("\n=== 测试获取对话列表 ===")
    
    # 测试参数
    user_id = "test_user_123"  # 替换为实际的用户ID
    page = 1
    size = 10
    
    print(f"测试参数: user_id={user_id}, page={page}, size={size}")
    
    try:
        # 调用函数
        print("正在调用 get_conversations_by_user_id...")
        conversations, total = get_conversations_by_user_id(user_id, page, size)
        
        print(f"✓ 调用成功!")
        print(f"总记录数: {total}")
        print(f"返回的对话数量: {len(conversations)}")
        
        # 打印前几个对话的详细信息
        for i, conv in enumerate(conversations[:3]):
            print(f"\n对话 {i+1}:")
            print(f"  ID: {conv['id']}")
            print(f"  名称: {conv['name']}")
            print(f"  最新消息: {conv['latestMessage'][:50]}..." if len(conv['latestMessage']) > 50 else f"  最新消息: {conv['latestMessage']}")
            print(f"  创建时间: {conv['createTime']}")
            print(f"  更新时间: {conv['updateTime']}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_get_messages():
    """测试获取消息功能"""
    print("\n=== 测试获取消息 ===")
    
    # 测试参数 - 需要替换为实际的对话ID
    conversation_id = "test_conversation_123"  # 替换为实际的对话ID
    
    print(f"测试参数: conversation_id={conversation_id}")
    
    try:
        # 调用函数
        print("正在调用 get_messages_by_conversation_id...")
        conversation, total = get_messages_by_conversation_id(conversation_id)
        
        if conversation:
            print(f"✓ 调用成功!")
            print(f"对话ID: {conversation['id']}")
            print(f"消息总数: {total}")
            if conversation['messages']:
                print(f"消息内容预览: {str(conversation['messages'][:2])[:100]}...")
            else:
                print("消息内容: 无消息")
        else:
            print("未找到对话")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def interactive_debug():
    """交互式调试模式"""
    print("\n=== 交互式调试模式 ===")
    print("你可以在这里设置断点并进行调试")
    print("可用的调试命令:")
    print("  n (next) - 执行下一行")
    print("  s (step) - 步入函数")
    print("  c (continue) - 继续执行")
    print("  l (list) - 显示当前代码")
    print("  p variable_name - 打印变量值")
    print("  q (quit) - 退出调试")
    
    # 设置断点
    pdb.set_trace()
    
    # 测试代码
    user_id = "debug_user_123"
    conversations, total = get_conversations_by_user_id(user_id, 1, 5)
    print(f"调试结果: {len(conversations)} 个对话")

if __name__ == "__main__":
    print("🚀 开始调试 conversation service...")
    print("=" * 60)
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ 检测到虚拟环境")
    else:
        print("⚠️  未检测到虚拟环境，建议激活虚拟环境")
    
    # 测试获取对话列表
    test_get_conversations()
    
    print("\n" + "="*60 + "\n")
    
    # 测试获取消息
    test_get_messages()
    
    print("\n" + "="*60)
    print("🎯 调试完成!")
    
    # 询问是否进入交互式调试
    try:
        response = input("\n是否进入交互式调试模式? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            interactive_debug()
    except KeyboardInterrupt:
        print("\n用户取消交互式调试")
