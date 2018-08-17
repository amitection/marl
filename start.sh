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

python3 main.py --agentname A11 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A12 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A13 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A14 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A15 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A16 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A17 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A18 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A19 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A20 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A21 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > output/p21.log 2>&1 &
python3 main.py --agentname A22 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A23 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A24 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A25 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A26 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A27 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A28 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A29 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A30 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A31 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > output/p31.log 2>&1 &
python3 main.py --agentname A32 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A33 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A34 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A35 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A36 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A37 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A38 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A39 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A40 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A41 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > output/p41.log 2>&1 &
python3 main.py --agentname A42 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A43 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A44 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A45 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &

python3 main.py --agentname A46 --nameserver 127.0.0.1:10000 --battInit 7.5 --nSolarPanel 72 > /dev/null 2>&1 &
python3 main.py --agentname A47 --nameserver 127.0.0.1:10000 --battInit 2.5 --nSolarPanel 54 > /dev/null 2>&1 &
python3 main.py --agentname A48 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > /dev/null 2>&1 &
python3 main.py --agentname A49 --nameserver 127.0.0.1:10000 --battInit 0.0 --nSolarPanel 0 > /dev/null 2>&1 &
python3 main.py --agentname A50 --nameserver 127.0.0.1:10000 --battInit 5.0 --nSolarPanel 12 > output/p50.log 2>&1 &
