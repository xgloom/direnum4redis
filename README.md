# DirEnum4Redis
_A simple script to find directories in Redis._

This script was built by modifying [n0b0dyCNs implementation](https://github.com/n0b0dyCN/redis-rogue-server); which uses sockets to interact with Redis. 

## Requirements
Python 3.6+

## Usage
```
Usage: direnum4redis.py [options]

Options:
  -h, --help  show this help message and exit
  --rhost=RH  target host
  --rport=RP  target redis port, default 6379
  --auth=PW   authentication string
  --dir=CD    directory to fuzz, default /
  --wlist=WL  wordlist directory
```
