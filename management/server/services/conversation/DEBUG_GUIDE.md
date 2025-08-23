# Python调试指南

## 1. 使用Python内置调试器（pdb）

### 方法1：在代码中添加断点

```python
import pdb

def your_function():
    pdb.set_trace()  # 程序会在这里暂停
    # 你的代码
```

### 方法2：使用pdb命令行调试

```bash
# 激活虚拟环境
source ../../venv/bin/activate

# 使用pdb运行脚本
python -m pdb debug_service.py
```

### pdb常用命令

- `n` (next) - 执行下一行
- `s` (step) - 步入函数
- `c` (continue) - 继续执行
- `l` (list) - 显示当前代码
- `p variable_name` - 打印变量值
- `q` (quit) - 退出调试
- `h` (help) - 显示帮助

## 2. 使用VS Code调试

### 步骤1：打开VS Code
```bash
code .
```

### 步骤2：设置断点
1. 在代码行号左侧点击设置断点
2. 或者使用 `F9` 快捷键

### 步骤3：启动调试
1. 按 `F5` 或点击调试按钮
2. 选择 "Debug Conversation Service" 配置

### 步骤4：调试控制
- `F5` - 继续执行
- `F10` - 单步跳过
- `F11` - 单步进入
- `Shift+F11` - 单步跳出
- `F9` - 切换断点

## 3. 使用调试脚本

### 运行完整调试脚本
```bash
# 激活虚拟环境
source ../../venv/bin/activate

# 运行调试脚本
cd management/server/services/conversation
python debug_service.py
```

### 运行快速调试脚本
```bash
# 激活虚拟环境
source ../../venv/bin/activate

# 运行快速调试
cd management/server/services/conversation
python quick_debug.py
```

## 4. 调试技巧

### 4.1 打印调试信息
```python
print(f"调试信息: {variable_name}")
```

### 4.2 使用logging模块
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"调试信息: {variable_name}")
```

### 4.3 条件断点
```python
if some_condition:
    pdb.set_trace()
```

## 5. 常见问题解决

### 5.1 模块导入错误
```bash
# 确保在正确的目录下运行
cd management/server

# 设置PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 5.2 虚拟环境问题
```bash
# 检查虚拟环境
which python

# 激活虚拟环境
source ../../venv/bin/activate
```

### 5.3 数据库连接问题
```python
# 检查数据库配置
print(DB_CONFIG)

# 测试数据库连接
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("数据库连接成功")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

## 6. 调试最佳实践

1. **从小开始**：先测试简单的功能
2. **使用断点**：在关键位置设置断点
3. **检查变量**：经常检查变量值
4. **记录日志**：使用print或logging记录关键信息
5. **分步调试**：一次只调试一个功能
6. **清理代码**：调试完成后移除调试代码

## 7. 调试配置文件

VS Code调试配置已保存在 `.vscode/launch.json` 中，包含：
- Debug Conversation Service
- Debug Service Directly
- Python Debugger: Current File

## 8. 快速调试命令

```bash
# 快速测试
cd management/server/services/conversation
source ../../../venv/bin/activate
python quick_debug.py

# 完整调试
python debug_service.py

# 使用pdb
python -m pdb debug_service.py
```
