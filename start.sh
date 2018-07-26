#!/usr/bin/env bash
python synchronizer.py --agentname Steve --nameserver 127.0.0.1:10000 > sync.log 2>&1 &
python main.py --agentname Alice --tag mk1 --nameserver 127.0.0.1:10000 --allies Bob,Charlie --battInit 7.2 --nSolarPanel 72 > p1.log 2>&1 &
python main.py --agentname Bob --tag mk1 --nameserver 127.0.0.1:10000 --allies Alice,Charlie --battInit 2.5 --nSolarPanel 72 > p2.log 2>&1 &
python main.py --agentname Charlie --tag mk1 --nameserver 127.0.0.1:10000 --allies Alice,Bob --battInit 5.0 --nSolarPanel 18 > p3.log 2>&1 &