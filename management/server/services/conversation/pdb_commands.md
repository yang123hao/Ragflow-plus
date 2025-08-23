# PDB调试命令参考

## 基本命令

### 执行控制
- `n` (next) - 执行下一行代码
- `s` (step) - 步入函数（进入函数内部）
- `c` (continue) - 继续执行直到下一个断点
- `r` (return) - 继续执行直到当前函数返回
- `q` (quit) - 退出调试器

### 查看代码
- `l` (list) - 显示当前代码位置周围的代码
- `ll` (longlist) - 显示当前函数的所有代码
- `w` (where) - 显示当前调用栈

### 查看变量
- `p variable_name` - 打印变量值
- `pp variable_name` - 美化打印变量值
- `whatis variable_name` - 显示变量类型

### 设置断点
- `b line_number` - 在指定行设置断点
- `b function_name` - 在函数开始处设置断点
- `cl` (clear) - 清除所有断点
- `cl line_number` - 清除指定行的断点

### 其他命令
- `h` (help) - 显示帮助信息
- `h command` - 显示特定命令的帮助
- `!command` - 执行Python命令
- `a` (args) - 显示当前函数的参数

## 常用调试流程

1. **开始调试**：
   ```bash
   python -m pdb debug_service.py
   ```

2. **查看当前代码**：
   ```
   (Pdb) l
   ```

3. **执行下一行**：
   ```
   (Pdb) n
   ```

4. **查看变量值**：
   ```
   (Pdb) p user_id
   (Pdb) p page
   ```

5. **继续执行**：
   ```
   (Pdb) c
   ```

## 示例调试会话

```
$ python -m pdb debug_service.py
> /path/to/debug_service.py(3)<module>()
-> """
(Pdb) n
> /path/to/debug_service.py(4)<module>()
-> 调试脚本 - 用于测试conversation service
(Pdb) n
> /path/to/debug_service.py(5)<module>()
-> 使用方法：
(Pdb) c
正在导入模块...
✓ 模块导入成功!
=== 测试获取对话列表 ===
测试参数: user_id=test_user_123, page=1, size=10
正在调用 get_conversations_by_user_id...
> /path/to/service.py(23)get_conversations_by_user_id()
-> try:
(Pdb) p user_id
'test_user_123'
(Pdb) n
> /path/to/service.py(24)get_conversations_by_user_id()
-> conn = mysql.connector.connect(**DB_CONFIG)
(Pdb) c
```

## 调试技巧

1. **使用 `!` 执行Python代码**：
   ```
   (Pdb) !print("Hello World")
   (Pdb) !import sys; print(sys.path)
   ```

2. **查看复杂对象**：
   ```
   (Pdb) pp result
   (Pdb) p dir(result)
   ```

3. **设置条件断点**：
   ```python
   # 在代码中添加
   if user_id == "specific_user":
       pdb.set_trace()
   ```

4. **调试循环**：
   ```python
   for i, item in enumerate(items):
       if i == 5:  # 在第6次迭代时暂停
           pdb.set_trace()
       print(item)
   ```









