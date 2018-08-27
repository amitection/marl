#!/usr/bin/env bash
python3 synchronizer.py --agentname Steve --nameserver 127.0.0.1:10000 > sync.log 2>&1 &
python3 main.py --agentname A1 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > output/p1.log 2>&1 &
python3 main.py --agentname A2 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > output/p2.log 2>&1 &
python3 main.py --agentname A3 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A4 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A5 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > output/p5.log 2>&1 &

python3 main.py --agentname A6 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A7 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A8 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A9 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > output/p9.log 2>&1 &
python3 main.py --agentname A10 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > output/p10.log 2>&1 &
