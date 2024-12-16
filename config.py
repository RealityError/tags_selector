# -*- coding: utf-8 -*-
# @Time : 2023/1/18
# @Author : 白猫猫
# @File : config.py
# @Software: Vscode|虚拟环境|3.10.6|64-bit
"""
该模块定义了存储运行设置的变量。
"""


import yaml

config: dict = {}
"""变量存储对象。

默认信息:
- 格式: dict

用法:
python
    ```
    from config import config
    ```
"""


def load_config(file_path: str) -> dict:
    """加载配置文件到全局变量 `config` 中。

    Args:
        file_path (str): 配置文件路径。
    
    Returns:
        dict: 加载的配置字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
            return loaded_config
    except FileNotFoundError:
        raise

        

# 加载配置文件
config = load_config('./config.yaml')
