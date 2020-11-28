#!/usr/bin/env bash

#wget https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz
#pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 一个检测, 后面串联多个不同语言识别模型
reco_language="ch,japan,en,korean"
port="8811"
ps aux |grep "ocr_server_${reco_language}_${port}" |awk -F ' ' '{print $2}' |xargs -i kill -9 {}
nohup python ocr_server.py --gpu 0 --port ${port} --rec ${reco_language} >/dev/null 2>&1 &
echo "查看是否启动成功: tail -f log/ocr_${port}.log"


reco_language="japan"
port="8812"
ps aux |grep "ocr_server_${reco_language}_${port}" |awk -F ' ' '{print $2}' |xargs -i kill -9 {}
nohup python ocr_server.py --gpu 0 --port ${port} --rec ${reco_language} >/dev/null 2>&1 &
echo "查看是否启动成功: tail -f log/ocr_${port}.log"

