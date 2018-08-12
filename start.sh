#!/usr/bin/env bash
python3 synchronizer.py --agentname Steve --nameserver 127.0.0.1:10000 > sync.log 2>&1 &
python3 main.py --agentname Alice --nameserver 127.0.0.1:10000 --allies Bob,Charlie,Dave,Ellie --battInit 7.5 --nSolarPanel 72 > p1.log 2>&1 &
python3 main.py --agentname Bob --nameserver 127.0.0.1:10000 --allies Alice,Charlie,Dave,Ellie --battInit 2.5 --nSolarPanel 54 > p2.log 2>&1 &
python3 main.py --agentname Charlie --nameserver 127.0.0.1:10000 --allies Alice,Bob,Dave,Ellie --battInit 5.0 --nSolarPanel 12 > p3.log 2>&1 &
python3 main.py --agentname Dave --nameserver 127.0.0.1:10000 --allies Alice,Bob,Charlie,Ellie --battInit 0.0 --nSolarPanel 0 > p4.log 2>&1 &
python3 main.py --agentname Ellie --nameserver 127.0.0.1:10000 --allies Alice,Bob,Charlie,Dave --battInit 5.0 --nSolarPanel 12 > p5.log 2>&1 &