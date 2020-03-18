# -*- coding:utf-8 -*-
import re, sys
from ..manager import config
from ..core.python import *

class Node:

    def __init__(self):
        super().__init__()

        # 配置标记值（不能重复）
        self.id = None

        # 节点对应的实体路径
        self.entry = None

        # 开发模式，如果不配置，则代表任何模式都启用，否则只有命中的模式才启用
        self.enable = None

class Attribute:

    @staticmethod
    def ToString(v):
        return ",".join(v)

    @staticmethod
    def FromString(v):
        return v.split(",")

def NodeIsEnable(node):
    """判断此Node节点是否可用"""
    if not node['enable']:
        return True
    conds = node['enable'].split(",")
    # 找到一个满足的即为满足
    for e in conds:
        if not e:
            continue

        # 仅--debug打开
        if e == "debug":
            return config.DEBUG
        # 仅--develop打开
        if e == "develop":
            return config.DEVELOP
        # 仅--publish打开
        if e == "publish":
            return config.PUBLISH
        # 仅--distribution打开
        if e == "distribution":
            return config.DISTRIBUTION
        # 处于publish或distribution打开
        if e == "release":
            return config.PUBLISH or config.DISTRIBUTION
        # 运行在devops容器中
        if e == "devops":
            return config.DEVOPS
        # 容器内网测试版
        if e == "devops-develop" or e == "devopsdevelop":
            return config.DEVOPS_DEVELOP
        # 容器发布版本
        if e == "devops-release" or e == "devopsrelease":
            return config.DEVOPS_RELEASE
        # 本地运行
        if e == "local":
            return config.LOCAL
        
        if indexOf(sys.argv, '--' + e) != -1:
            return True
    return False
