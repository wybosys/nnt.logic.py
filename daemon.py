#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from app.main import launch

if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        launch()
