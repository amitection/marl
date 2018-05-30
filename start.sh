python main.py --agentname Alice --nameserver 127.0.0.1:10000 > p1.log 2>&1 &
sleep 1
python main.py --agentname Bob --nameserver 127.0.0.1:10000 > p2.log 2>&1 &