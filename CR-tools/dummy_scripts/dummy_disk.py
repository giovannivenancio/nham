#!/usr/bin/env python
import time

i = 0

while True:
    i += 1

    with open('dummy_logger', 'a') as f:
        f.write(str(i) + '\n')

    time.sleep(1)
