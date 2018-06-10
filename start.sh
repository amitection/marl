#!/usr/bin/env bash
python main.py --agentname Alice --nameserver 127.0.0.1:10000 --allies Bob > p1.log 2>&1 &
sleep 1.5
python main.py --agentname Bob --nameserver 127.0.0.1:10000 --allies Alice > p2.log 2>&1 &