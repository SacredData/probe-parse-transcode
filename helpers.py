import json
import os
import subprocess as sp
import yaml

# Global config yaml
cfile = open('probe/config.yaml', 'r')
cconfig = yaml.load_all(cfile)
for data in cconfig:
    c = data


def analyze(source_file):
    """
    Run analysis on the input file, ensuring that the media file
    contains a valid video stream. The data collected from this
    analysis is to inform all other methods within this class.
    """
    # If the file can be opened we may begin analyzing the container
    fo = open(c['analysis_logs_dir'] + os.path.split(source_file)[1] +
              '.data', 'w')
    analyze = ['ffprobe', '-v', 'quiet', '-show_format', '-show_streams',
               '-print_format', 'json', source_file]
    probe_data = sp.check_output(analyze, bufsize=10**8, stderr=sp.STDOUT)
    probe_res = json.loads(
        probe_data.decode(encoding='UTF-8'), 'latin-1')
    # j = json.loads(probe_res['streams'])
    json.dump(probe_res, fo)
    return probe_res
