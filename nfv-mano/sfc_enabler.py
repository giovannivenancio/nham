#! /usr/bin/env python3

import sys
from socket import *

port = 10000

#BUFSIZE = 512
#BUFSIZE = 4096
BUFSIZE = 8192

if __name__ == "__main__":
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(("", port))
    s.listen(1)

    print("Listening...")

    while True:
        conn, (host, remoteport) = s.accept()

        while True:
            data = conn.recv(BUFSIZE)

            if not data:
                break

            # send data back to VNF
            conn.send(data)

            del data

        return_message = "OK!\n"
        conn.send(return_message.encode('utf-8'))
        conn.close()

        print ("Done with", host, "port", remoteport)
