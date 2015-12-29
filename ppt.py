#!/usr/bin/env python
import argparse
import json
import logging
import Queue
import sys
import subprocess as sp
import threading
import yaml
# from analyze import analyze

# Instantiate logger
logging.basicConfig(filename='ppt.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
q = Queue.Queue()
logging.info('Task queue instantiated')
# Global config yaml
cfile = open('probe/config.yaml', 'r')
cconfig = yaml.load_all(cfile)
for data in cconfig:
    c = data
logging.info('Loaded global config from config.yaml')


def build_y4m(source_file):
    """
    Create the Y4M file, which will serve as the reference video data
    from which we will make our reference VP8 and VP9 streams.
    """
    y4m_start = ['ffmpeg', '-y', '-i', source_file]
    y4m_codec = c['formats']['y4m']['codec'].split(' ')
    y4m_opts = c['formats']['y4m']['options'].split(' ')
    y4m_out = source_file + '.y4m'
    y4m_cmd = y4m_start + y4m_codec + y4m_opts + [y4m_out]
    print("Converting source video stream to Y4M rawvideo container.")
    try:
        sp.check_output(y4m_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit("Error: Y4M rawvideo generation failed. Cannot continue.")


def analyze(source_file):
    """
    Run analysis on the input file, ensuring that the media file
    contains a valid video stream. The data collected from this
    analysis is to inform all other methods within this class.
    """
    # If the file can be opened we may begin analyzing the container
    filename = str(source_file)
    analyze = ['ffprobe', '-v', 'quiet', '-show_format', '-show_streams',
               '-print_format', 'json', filename]
    probe_data = sp.check_output(analyze, bufsize=10**8, stderr=sp.STDOUT)
    probe_res = json.loads(
        probe_data.decode(encoding='UTF-8'), 'latin-1')
    logging.info(probe_data)
    stm_data = json.loads(probe_res['streams'])
    for stream in stm_data:
        print stream
        if stream['codec_type'] in 'video':
            video_stream = stream
            logging.info('Found video stream in file.')
        else:
            print 'No video!!!'
            return
    mbps = int(video_stream['bit_rate']) / 1000000
    # Determine new bitrate when source bit rate is too high to stream
    if mbps > 5:
        if mbps / 2 > 11:
            if mbps / 2 > 11 and mbps / 2 < 20:
                new_mbps = mbps / 2
            else:
                new_mbps = 14
        else:
            new_mbps = mbps / 2.25
    else:
        new_mbps = mbps
    if new_mbps > 8:
        new_mbps = round(new_mbps)
    else:
        new_mbps = round(new_mbps)
    # Determine minimum+maximum bit rate + buffer size
    target = new_mbps * 1000 * 1.5
    if video_stream['coded_height'] >= 1080:
        mult_begin = 'webm_1080'
    elif video_stream['coded_height'] >= 720:
        mult_begin = 'webm_720'
    elif video_stream['coded_height'] >= 480:
        mult_begin = 'webm_480'
    elif video_stream['coded_height'] >= 720:
        mult_begin = 'webm_360'
    else:
        mult_begin = 'webm_280'
    instructs = [target, mult_begin]
    return instructs


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
                try:
                    if int(task_cmd[0]) == 0:
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
