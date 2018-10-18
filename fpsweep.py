#!/usr/bin/env python                                          
# script by MikeT                                              
# ping a list of given subnets with threads for increase speed 
# use standard linux /bin/ping utility                         
# example python fpsweep.py -s 10.0.0. -r 1                    
# script ask for 3 input:                                      
#			1. -s class c subnet " 192.168.1. "                      
#			2. -r <1-254>                                            
#     3. -h --help                                             
#
from threading import Thread
import subprocess
import Queue
import re
import sys
import optparse
 
# some global vars
num_threads = 25
ping_q = Queue.Queue()
out_q = Queue.Queue()

#optparse
parser = optparse.OptionParser('Usage: -s <192.168.1.> -r <1-254>')
parser.add_option('-s', '--subnet', dest='subnet', type='string')
parser.add_option('-r', '--range', dest='ra')
(options, args)=parser.parse_args()
subnet = options.subnet
ra = options.ra
ra = ra.split('-')

# build IP array and name your target
ping = []
for i in range (int(ra[0]),int(ra[1])+1):
  ping.append(subnet+str(i))
 
# thread code : wraps system ping command
def thread_pinger(i, q):
  while True:
    ip = q.get()
    args=['/bin/ping', '-c', '1', '-W', '1', str(ip)]
    p_ping = subprocess.Popen(args,
                              shell=False,
                              stdout=subprocess.PIPE)
    # save ping stdout
    p_ping_out = p_ping.communicate()[0]
 
    if (p_ping.wait() == 0):
      # rtt min/avg/max/mdev = 22.293/22.293/22.293/0.000 ms
      search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',
                         p_ping_out, re.M|re.I)
      ping_rtt = search.group(2)

# print output format to screen
      out_q.put( str(ip) )
 
    # update queue : this ip is processed 
    q.task_done()
 
# start the thread pool
for i in range(num_threads):
  worker = Thread(target=thread_pinger, args=(i, ping_q))
  worker.setDaemon(True)
  worker.start()
 
# fill queue
for ip in ping:
  ping_q.put(ip)
 
# wait until worker threads are done to exit    
ping_q.join()
 
while True:
  try:
    msg = out_q.get_nowait()
  except Queue.Empty:
    break
  print msg