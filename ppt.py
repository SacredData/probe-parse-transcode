#!/usr/bin/env python
import argparse
import logging
import Queue
import threading


# Instantiate logger
logging.basicConfig(filename='ppt.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
q = Queue.Queue()
logging.info('Task queue instantiated')


class ComputerTasks(threading.Thread):

    "A threaded worker class which seeks to clear out the PPT task queue."

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        logging.info('New task thread established.')

    def run(self):
        logging.info('Task thread is running a command.')
        while 1:
            try:
                task_cmd = self.queue.get()
                print task_cmd
                try:
                    if int(task_cmd[0]) == 0:
                        from helpers import analyze
                        analyze(task_cmd[1])
                finally:
                    self.queue.task_done()
                    logging.info('Command cleaved from task queue: %s',
                                 task_cmd)
            except Queue.Empty:
                continue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    args = parser.parse_args()
    print args.file
    q.put([0, str(args.file)])
    print 'Queue size:'
    print q.qsize()
    for i in xrange(2):      # Two threads should do the trick
        t = ComputerTasks(q)
        t.setDaemon(True)    # Daemonize each threaded worker
        t.start()

main()
