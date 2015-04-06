#! /usr/bin/env python
# -*- coding: utf-8 -*-

import threading, time, Queue

def writer(queue):
    i = 0

    while True:
    	if not queue.empty():
    		i = queue.get()

    	print 'sub: %d' % i
    	time.sleep(1)

q = Queue.Queue()

# init threads
t1 = threading.Thread(target=writer, args=(q,))

# start threads
t1.start()

for i in xrange(20):
	q.put(i)
	time.sleep(2)