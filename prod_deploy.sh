#!/usr/bin/env bash

#pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ps aux |grep ocr_server.py |awk -F ' ' '{print $2}' |xargs -i kill -9 {}

# 一个检测, 后面串联多个不同语言识别模型

nohup python ocr_server.py --gpu 0 --port 8811 --rec "ch,japan,en,korean" >/dev/null 2>&1 &

echo "查看是否启动成功: tail -f log/ocr_8811.log"
