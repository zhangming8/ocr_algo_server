#!/usr/bin/env bash

#wget https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz
#pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 一个检测模型, 后面并联多个不同语言识别模型
reco_language="ch,japan,en,korean,ch_h,french, german"
port="8811"
gpu=0

ps aux |grep "ocr_server_${port}_${reco_language}" |awk -F ' ' '{print $2}' |xargs -i kill -9 {}
nohup python ocr_server.py --gpu ${gpu} --port ${port} --rec ${reco_language} >/dev/null 2>&1 &
echo "查看是否启动成功: tail -f log/ocr_${port}.log"


# 一个检测模型, 后面接一个语言识别模型
reco_language="ch,ch_h"
port="8812"
ps aux |grep "ocr_server_${port}_${reco_language}" |awk -F ' ' '{print $2}' |xargs -i kill -9 {}
nohup python ocr_server.py --gpu ${gpu} --port ${port} --rec ${reco_language} >/dev/null 2>&1 &
echo "查看是否启动成功: tail -f log/ocr_${port}.log"
