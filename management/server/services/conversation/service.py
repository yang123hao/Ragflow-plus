import mysql.connector
from database import DB_CONFIG
import pdb  # 添加pdb导入
import json  # 添加json导入


def get_conversations_by_user_id(user_id, page=1, size=20, sort_by="update_time", sort_order="desc", keyword=None):
    """
    根据用户ID获取对话列表，支持关键字搜索

    参数:
        user_id (str): 用户ID
        page (int): 当前页码
        size (int): 每页大小
        sort_by (str): 排序字段
        sort_order (str): 排序方式 (asc/desc)
        keyword (str): 搜索关键字，可选

    返回:
        tuple: (对话列表, 总数)
    """
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        print(f"user_id: {user_id}")
        # 直接使用user_id作为tenant_id
        tenant_id = user_id
        
        # 查询总记录数
        if keyword:
            count_sql = """
            SELECT COUNT(DISTINCT d.id) as total 
            FROM dialog d
            LEFT JOIN conversation c ON d.id = c.dialog_id
            WHERE d.tenant_id = %s 
            AND (d.name LIKE %s OR c.message LIKE %s)
            """
            search_pattern = f"%{keyword}%"
            cursor.execute(count_sql, (tenant_id, search_pattern, search_pattern))
        else:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM dialog d
            WHERE d.tenant_id = %s
            """
            cursor.execute(count_sql, (tenant_id,))
        
        total = cursor.fetchone()["total"]

        # print(f"查询到总记录数: {total}")

        # 计算分页偏移量
        offset = (page - 1) * size

        # 确定排序方向
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # 执行分页查询
        if keyword:
            query = f"""
            SELECT DISTINCT
                d.id, 
                d.name,
                d.create_date,
                d.update_date,
                d.tenant_id
            FROM 
                dialog d
            LEFT JOIN conversation c ON d.id = c.dialog_id
            WHERE 
                d.tenant_id = %s
                AND (d.name LIKE %s OR c.message LIKE %s)
            ORDER BY 
                d.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{keyword}%"
            print(f"执行关键字搜索查询: {query}")
            print(f"参数: tenant_id={tenant_id}, keyword={keyword}, size={size}, offset={offset}")
            cursor.execute(query, (tenant_id, search_pattern, search_pattern, size, offset))
        else:
            query = f"""
            SELECT 
                d.id, 
                d.name,
                d.create_date,
                d.update_date,
                d.tenant_id
            FROM 
                dialog d
            WHERE 
                d.tenant_id = %s
            ORDER BY 
                d.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            print(f"执行普通查询: {query}")
            print(f"参数: tenant_id={tenant_id}, size={size}, offset={offset}")
            cursor.execute(query, (tenant_id, size, offset))
        results = cursor.fetchall()

        print(f"查询结果数量: {len(results)}")

        # 获取每个对话的最新消息
        conversations = []
        for dialog in results:
            # 查询对话的所有消息
            conv_query = """
            SELECT id, message, name 
            FROM conversation 
            WHERE dialog_id = %s
            ORDER BY create_date DESC
            """
            cursor.execute(conv_query, (dialog["id"],))
            conv_results = cursor.fetchall()

            latest_message = ""
            conversation_name = dialog["name"]  # 默认使用dialog的name
            if conv_results and len(conv_results) > 0:
                # 获取最新的一条对话记录
                latest_conv = conv_results[0]
                # 如果conversation有name，优先使用conversation的name
                if latest_conv and latest_conv.get("name"):
                    conversation_name = latest_conv["name"]

                if latest_conv and latest_conv["message"]:
                    # 获取最后一条消息内容
                    messages = latest_conv["message"]
                    if messages and len(messages) > 0:
                        # 检查消息类型，处理字符串和字典两种情况
                        if isinstance(messages[-1], dict):
                            latest_message = messages[-1].get("content", "")
                        elif isinstance(messages[-1], str):
                            latest_message = messages[-1]
                        else:
                            latest_message = str(messages[-1])

            conversations.append(
                {
                    "id": dialog["id"],
                    "name": conversation_name,
                    "latestMessage": latest_message[:100] + "..." if len(latest_message) > 100 else latest_message,
                    "createTime": dialog["create_date"].strftime("%Y-%m-%d %H:%M:%S") if dialog["create_date"] else "",
                    "updateTime": dialog["update_date"].strftime("%Y-%m-%d %H:%M:%S") if dialog["update_date"] else "",
                }
            )

        # 关闭连接
        cursor.close()
        conn.close()

        return conversations, total

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        # 更详细的错误日志
        import traceback

        traceback.print_exc()
        return [], 0
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback

        traceback.print_exc()
        return [], 0


def get_messages_by_conversation_id(conversation_id, page=1, size=30):
    """
    获取特定对话的详细信息

    参数:
        conversation_id (str): 对话ID
        page (int): 当前页码
        size (int): 每页大小

    返回:
        tuple: (对话详情, 总数)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 先检查表结构
        try:
            cursor.execute("DESCRIBE conversation")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            print(f"conversation表字段: {column_names}")
        except Exception as e:
            print(f"检查表结构失败: {e}")
            column_names = []
        
        # 查询对话信息
        query = """
        SELECT *
        FROM conversation 
        WHERE id = %s
        ORDER BY create_date DESC
        """
        print(f"执行查询: {query}")
        print(f"参数: conversation_id={conversation_id}")
        cursor.execute(query, (conversation_id,))
        result = cursor.fetchall()  # 确保读取所有结果
        
        # 如果没有找到结果，尝试其他可能的表
        if not result:
            print(f"在conversation表中未找到ID: {conversation_id}")
            print("尝试在dialog表中查找...")
            
            # 尝试在dialog表中查找
            dialog_query = """
            SELECT *
            FROM dialog 
            WHERE id = %s
            ORDER BY create_date DESC
            """
            cursor.execute(dialog_query, (conversation_id,))
            dialog_result = cursor.fetchall()
            
            if dialog_result:
                print(f"在dialog表中找到记录: {dialog_result[0]}")
                # 如果找到dialog记录，尝试获取相关的conversation记录
                conv_query = """
                SELECT *
                FROM conversation 
                WHERE dialog_id = %s
                ORDER BY create_date DESC
                """
                cursor.execute(conv_query, (conversation_id,))
                conv_result = cursor.fetchall()
                
                if conv_result:
                    print(f"找到相关conversation记录: {len(conv_result)}条")
                    result = conv_result
                else:
                    print("未找到相关conversation记录")
                    result = dialog_result
            else:
                print("在dialog表中也未找到记录")
        
        print(f"查询结果数量: {len(result) if result else 0}")
        if result:
            print(f"第一条记录字段: {list(result[0].keys()) if result[0] else 'None'}")
            print(f"第一条记录内容: {result[0]}")

        if not result:
            print(f"未找到对话ID: {conversation_id}")
            cursor.close()
            conn.close()
            return None, 0

        # 获取第一条记录作为对话详情
        conversation = None
        if len(result) > 0:
            conversation = {
                "id": result[0]["id"],
                "tenantId": result[0].get("dialog_id", ""),  # 使用dialog_id作为tenantId
                "createTime": result[0]["create_date"].strftime("%Y-%m-%d %H:%M:%S") if result[0].get("create_date") else "",
                "updateTime": result[0]["update_date"].strftime("%Y-%m-%d %H:%M:%S") if result[0].get("update_date") else "",
                "messages": result[0].get("message", []),
            }

        # 打印调试信息
        print(f"获取到对话详情: ID={conversation_id}")
        print(f"消息长度: {len(conversation['messages']) if conversation and conversation.get('messages') else 0}")

        # 关闭连接
        cursor.close()
        conn.close()

        # 返回对话详情和消息总数
        total = len(conversation["messages"]) if conversation and conversation.get("messages") else 0
        
        # 将消息数据转换为前端期望的格式
        messages_list = []
        print(f"开始处理消息数据...")
        print(f"conversation对象: {conversation}")
        print(f"messages字段类型: {type(conversation.get('messages')) if conversation else 'None'}")
        print(f"messages字段内容: {conversation.get('messages') if conversation else 'None'}")
        
        if conversation and conversation.get("messages"):
            messages = conversation["messages"]
            print(f"原始messages: {messages}")
            print(f"messages类型: {type(messages)}")
            
            if isinstance(messages, str):
                print(f"messages是字符串，尝试JSON解析...")
                try:
                    messages = json.loads(messages)
                    print(f"JSON解析成功: {messages}")
                except Exception as e:
                    print(f"JSON解析失败: {e}")
                    messages = []
            
            if isinstance(messages, list):
                print(f"messages是列表，长度: {len(messages)}")
                for i, msg in enumerate(messages):
                    print(f"处理第{i}条消息: {msg}")
                    if isinstance(msg, dict):
                        messages_list.append({
                            "id": msg.get("id", f"msg-{i}"),
                            "conversation_id": conversation_id,
                            "role": msg.get("role", "unknown"),
                            "content": msg.get("content", ""),
                            "create_time": msg.get("created_at", conversation["createTime"])
                        })
                    elif isinstance(msg, str):
                        messages_list.append({
                            "id": f"msg-{i}",
                            "conversation_id": conversation_id,
                            "role": "user",
                            "content": msg,
                            "create_time": conversation["createTime"]
                        })
            else:
                print(f"messages不是列表，类型: {type(messages)}")
        else:
            print(f"没有找到messages字段或conversation对象")
        
        print(f"最终生成的消息列表: {messages_list}")
        print(f"消息总数: {total}")
        return messages_list, total

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        # 更详细的错误日志
        import traceback

        traceback.print_exc()
        return None, 0
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback

        traceback.print_exc()
        return None, 0


def search_all_conversations(keyword=None, page=1, size=20, sort_by="update_time", sort_order="desc"):
    """
    全局搜索所有用户的对话，支持关键字搜索

    参数:
        keyword (str): 搜索关键字，可选
        page (int): 当前页码
        size (int): 每页大小
        sort_by (str): 排序字段
        sort_order (str): 排序方式 (asc/desc)

    返回:
        tuple: (对话列表, 总数)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print(f"全局搜索，关键字: {keyword}")
        
        # 查询总记录数
        if keyword:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            WHERE (c.name LIKE %s OR c.message LIKE %s)
            """
            search_pattern = f"%{keyword}%"
            cursor.execute(count_sql, (search_pattern, search_pattern))
        else:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            """
            cursor.execute(count_sql)
        
        total = cursor.fetchone()["total"]
        print(f"查询到总记录数: {total}")

        # 计算分页偏移量
        offset = (page - 1) * size

        # 确定排序方向
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # 执行分页查询
        if keyword:
            query = f"""
            SELECT 
                c.id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id
            FROM 
                conversation c
            WHERE (c.name LIKE %s OR c.message LIKE %s)
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{keyword}%"
            print(f"执行全局关键字搜索查询: {query}")
            print(f"参数: keyword={keyword}, size={size}, offset={offset}")
            cursor.execute(query, (search_pattern, search_pattern, size, offset))
        else:
            query = f"""
            SELECT 
                c.id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id
            FROM 
                conversation c
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            print(f"执行全局普通查询: {query}")
            print(f"参数: size={size}, offset={offset}")
            cursor.execute(query, (size, offset))
        
        results = cursor.fetchall()
        print(f"查询结果数量: {len(results)}")

        # 获取每个对话的最新消息
        conversations = []
        for conversation in results:
            print(f"处理对话: {conversation}")
            
            # 查询对话的所有消息
            conv_query = """
            SELECT id, message, name 
            FROM conversation 
            WHERE id = %s
            ORDER BY create_date DESC
            """
            cursor.execute(conv_query, (conversation["id"],))
            conv_results = cursor.fetchall()

            latest_message = ""
            conversation_name = conversation.get("name", "")  # 默认使用conversation的name
            
            if conv_results and len(conv_results) > 0:
                # 获取最新的一条对话记录
                latest_conv = conv_results[0]
                print(f"最新对话记录: {latest_conv}")
                
                # 如果conversation有name，优先使用conversation的name
                if latest_conv and latest_conv.get("name"):
                    conversation_name = latest_conv["name"]

                if latest_conv and latest_conv["message"]:
                    # 获取最后一条消息内容
                    messages = latest_conv["message"]
                    print(f"消息字段: {messages}, 类型: {type(messages)}")
                    
                    if messages:
                        # 检查消息类型，处理字符串和字典两种情况
                        if isinstance(messages, str):
                            # 如果是字符串，尝试JSON解析
                            try:
                                import json
                                parsed_messages = json.loads(messages)
                                if isinstance(parsed_messages, list) and len(parsed_messages) > 0:
                                    latest_message = parsed_messages[-1].get("content", "")
                                else:
                                    latest_message = parsed_messages.get("content", "") if isinstance(parsed_messages, dict) else str(parsed_messages)
                            except:
                                latest_message = messages
                        elif isinstance(messages, list) and len(messages) > 0:
                            # 如果是列表
                            if isinstance(messages[-1], dict):
                                latest_message = messages[-1].get("content", "")
                            elif isinstance(messages[-1], str):
                                latest_message = messages[-1]
                            else:
                                latest_message = str(messages[-1])
                        elif isinstance(messages, dict):
                            # 如果是字典
                            latest_message = messages.get("content", "")
                        else:
                            latest_message = str(messages)
                    
                    print(f"提取的最新消息: {latest_message}")

            # 如果没有提取到消息内容，使用对话名称作为备选
            if not latest_message:
                latest_message = conversation_name or f"对话 {conversation['id']}"
            
            print(f"最终使用的消息内容: {latest_message}")

            conversations.append(
                {
                    "id": conversation["id"],
                    "content": latest_message[:200] + "..." if len(latest_message) > 200 else latest_message,  # 添加content字段
                    "name": conversation_name,
                    "latestMessage": latest_message[:100] + "..." if len(latest_message) > 100 else latest_message,
                    "createTime": conversation.get("create_date", "").strftime("%Y-%m-%d %H:%M:%S") if conversation.get("create_date") else "",
                    "tenantId": conversation.get("dialog_id", ""),  # 使用dialog_id作为tenantId
                }
            )

        # 关闭连接
        cursor.close()
        conn.close()

        return conversations, total

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        # 更详细的错误日志
        import traceback
        traceback.print_exc()
        return [], 0
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback
        traceback.print_exc()
        return [], 0


def search_all_conversations2(keyword=None, page=1, size=20, sort_by="update_time", sort_order="desc"):
    """
    全局搜索所有用户的对话，支持关键字搜索

    参数:
        keyword (str): 搜索关键字，可选
        page (int): 当前页码
        size (int): 每页大小
        sort_by (str): 排序字段
        sort_order (str): 排序方式 (asc/desc)

    返回:
        tuple: (对话列表, 总数)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print(f"全局搜索，关键字: {keyword}")
        
        # 查询总记录数
        if keyword:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE jt.content LIKE %s 
            """
            search_pattern = f"%{keyword}%"
            cursor.execute(count_sql, (search_pattern,))  # 只传入一个参数
        else:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            """
            cursor.execute(count_sql)
        
        total = cursor.fetchone()["total"]
        print(f"查询到总记录数: {total}")

        # 计算分页偏移量
        offset = (page - 1) * size

        # 确定排序方向
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # 执行分页查询
        if keyword:
            query = f"""
            SELECT 
                (select b.nickname  from user b where b.id=c.user_id) as id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id,
                jt.content,
                jt.role
            FROM 
                conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE jt.content LIKE %s 
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{keyword}%"
            print(f"执行全局关键字搜索查询: {query}")
            print(f"参数: keyword={keyword}, size={size}, offset={offset}")
            cursor.execute(query, (search_pattern, size, offset))
        else:
            query = f"""
            SELECT 
                (select b.nickname  from user b where b.id=c.user_id) as id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id,
                jt.content,
                jt.role
            FROM 
                conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            print(f"执行全局普通查询: {query}")
            print(f"参数: size={size}, offset={offset}")
            cursor.execute(query, (size, offset))
        
        results = cursor.fetchall()
        print(f"查询结果数量: {len(results)}")

        # 获取每个对话的最新消息
        conversations = []
        for conversation in results:
            print(f"处理对话: {conversation}")
            
            # 查询对话的所有消息
            conv_query = """
            SELECT (select b.nickname  from user b where b.id=c.user_id) as id, message, name,
            jt.content,
            jt.role,
            c.create_date,
            c.update_date
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE id = %s
            ORDER BY create_date DESC
            """
            cursor.execute(conv_query, (conversation["id"],))
            conv_results = cursor.fetchall()

            latest_message = ""
            conversation_name = conversation.get("name", "")  # 默认使用conversation的name
            
            if conv_results and len(conv_results) > 0:
                # 获取最新的一条对话记录
                latest_conv = conv_results[0]
                print(f"最新对话记录: {latest_conv}")
                
                # 如果conversation有name，优先使用conversation的name
                if latest_conv and latest_conv.get("name"):
                    conversation_name = latest_conv["name"]

                if latest_conv and latest_conv["message"]:
                    # 获取最后一条消息内容
                    messages = latest_conv["message"]
                    print(f"消息字段: {messages}, 类型: {type(messages)}")
                    
                    if messages:
                        # 检查消息类型，处理字符串和字典两种情况
                        if isinstance(messages, str):
                            # 如果是字符串，尝试JSON解析
                            try:
                                import json
                                parsed_messages = json.loads(messages)
                                if isinstance(parsed_messages, list) and len(parsed_messages) > 0:
                                    latest_message = parsed_messages[-1].get("content", "")
                                else:
                                    latest_message = parsed_messages.get("content", "") if isinstance(parsed_messages, dict) else str(parsed_messages)
                            except:
                                latest_message = messages
                        elif isinstance(messages, list) and len(messages) > 0:
                            # 如果是列表
                            if isinstance(messages[-1], dict):
                                latest_message = messages[-1].get("content", "")
                            elif isinstance(messages[-1], str):
                                latest_message = messages[-1]
                            else:
                                latest_message = str(messages[-1])
                        elif isinstance(messages, dict):
                            # 如果是字典
                            latest_message = messages.get("content", "")
                        else:
                            latest_message = str(messages)
                    
                    print(f"提取的最新消息: {latest_message}")

            # 如果没有提取到消息内容，使用对话名称作为备选
            if not latest_message:
                latest_message = conversation_name or f"对话 {conversation['id']}"
            
            print(f"最终使用的消息内容: {latest_message}")

            conversations.append(
                {
                    "id": conversation["id"],
                    "content": conversation["content"],  # 添加content字段
                    "name": conversation_name,
                    "role": conversation["role"],
                    "createTime": conversation.get("create_date", "").strftime("%Y-%m-%d %H:%M:%S") if conversation.get("create_date") else "",
                    "updateTime": conversation.get("update_date", "").strftime("%Y-%m-%d %H:%M:%S") if conversation.get("update_date") else "",
                }
            )

        # 关闭连接
        cursor.close()
        conn.close()

        return conversations, total

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        # 更详细的错误日志
        import traceback
        traceback.print_exc()
        return [], 0
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback
        traceback.print_exc()
        return [], 0

def test_update_git(keyword=None, page=1, size=20, sort_by="update_time", sort_order="desc"):
    """
    全局搜索所有用户的对话，支持关键字搜索

    参数:
        keyword (str): 搜索关键字，可选
        page (int): 当前页码
        size (int): 每页大小
        sort_by (str): 排序字段
        sort_order (str): 排序方式 (asc/desc)

    返回:
        tuple: (对话列表, 总数)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print(f"全局搜索，关键字: {keyword}")
        
        # 查询总记录数
        if keyword:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE jt.content LIKE %s 
            """
            search_pattern = f"%{keyword}%"
            cursor.execute(count_sql, (search_pattern,))  # 只传入一个参数
        else:
            count_sql = """
            SELECT COUNT(*) as total 
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            """
            cursor.execute(count_sql)
        
        total = cursor.fetchone()["total"]
        print(f"查询到总记录数: {total}")

        # 计算分页偏移量
        offset = (page - 1) * size

        # 确定排序方向
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # 执行分页查询
        if keyword:
            query = f"""
            SELECT 
                (select b.nickname  from user b where b.id=c.user_id) as id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id,
                jt.content,
                jt.role
            FROM 
                conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE jt.content LIKE %s 
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{keyword}%"
            print(f"执行全局关键字搜索查询: {query}")
            print(f"参数: keyword={keyword}, size={size}, offset={offset}")
            cursor.execute(query, (search_pattern, size, offset))
        else:
            query = f"""
            SELECT 
                (select b.nickname  from user b where b.id=c.user_id) as id, 
                c.name,
                c.create_date,
                c.update_date,
                c.dialog_id,
                jt.content,
                jt.role
            FROM 
                conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            ORDER BY 
                c.{sort_by} {sort_direction}
            LIMIT %s OFFSET %s
            """
            print(f"执行全局普通查询: {query}")
            print(f"参数: size={size}, offset={offset}")
            cursor.execute(query, (size, offset))
        
        results = cursor.fetchall()
        print(f"查询结果数量: {len(results)}")

        # 获取每个对话的最新消息
        conversations = []
        for conversation in results:
            print(f"处理对话: {conversation}")
            
            # 查询对话的所有消息
            conv_query = """
            SELECT (select b.nickname  from user b where b.id=c.user_id) as id, message, name,
            jt.content,
            jt.role,
            c.create_date,
            c.update_date
            FROM conversation c
            CROSS JOIN JSON_TABLE(c.message, '$[*]' COLUMNS (
            content JSON PATH '$.content',  
            role VARCHAR(50) PATH '$.role'  
            )) AS jt
            WHERE id = %s
            ORDER BY create_date DESC
            """
            cursor.execute(conv_query, (conversation["id"],))
            conv_results = cursor.fetchall()

            latest_message = ""
            conversation_name = conversation.get("name", "")  # 默认使用conversation的name
            
            if conv_results and len(conv_results) > 0:
                # 获取最新的一条对话记录
                latest_conv = conv_results[0]
                print(f"最新对话记录: {latest_conv}")
                
                # 如果conversation有name，优先使用conversation的name
                if latest_conv and latest_conv.get("name"):
                    conversation_name = latest_conv["name"]

                if latest_conv and latest_conv["message"]:
                    # 获取最后一条消息内容
                    messages = latest_conv["message"]
                    print(f"消息字段: {messages}, 类型: {type(messages)}")
                    
                    if messages:
                        # 检查消息类型，处理字符串和字典两种情况
                        if isinstance(messages, str):
                            # 如果是字符串，尝试JSON解析
                            try:
                                import json
                                parsed_messages = json.loads(messages)
                                if isinstance(parsed_messages, list) and len(parsed_messages) > 0:
                                    latest_message = parsed_messages[-1].get("content", "")
                                else:
                                    latest_message = parsed_messages.get("content", "") if isinstance(parsed_messages, dict) else str(parsed_messages)
                            except:
                                latest_message = messages
                        elif isinstance(messages, list) and len(messages) > 0:
                            # 如果是列表
                            if isinstance(messages[-1], dict):
                                latest_message = messages[-1].get("content", "")
                            elif isinstance(messages[-1], str):
                                latest_message = messages[-1]
                            else:
                                latest_message = str(messages[-1])
                        elif isinstance(messages, dict):
                            # 如果是字典
                            latest_message = messages.get("content", "")
                        else:
                            latest_message = str(messages)
                    
                    print(f"提取的最新消息: {latest_message}")

            # 如果没有提取到消息内容，使用对话名称作为备选
            if not latest_message:
                latest_message = conversation_name or f"对话 {conversation['id']}"
            
            print(f"最终使用的消息内容: {latest_message}")

            conversations.append(
                {
                    "id": conversation["id"],
                    "content": conversation["content"],  # 添加content字段
                    "name": conversation_name,
                    "role": conversation["role"],
                    "createTime": conversation.get("create_date", "").strftime("%Y-%m-%d %H:%M:%S") if conversation.get("create_date") else "",
                    "updateTime": conversation.get("update_date", "").strftime("%Y-%m-%d %H:%M:%S") if conversation.get("update_date") else "",
                }
            )

        # 关闭连接
        cursor.close()
        conn.close()

        return conversations, total

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        # 更详细的错误日志
        import traceback
        traceback.print_exc()
        return [], 0
    except Exception as e:
        print(f"未知错误: {e}")
        import traceback
        traceback.print_exc()
        return [], 0
