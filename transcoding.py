import os
import sys
import subprocess as sp
import yaml

# Transcoding config yaml
tfile = open('probe/transcoding.yaml', 'r')
tconfig = yaml.load_all(tfile)
for datat in tconfig:
    t = datat
cfile = open('probe/config.yaml', 'r')
cconfig = yaml.load_all(cfile)
for datac in cconfig:
    c = datac


def build_y4m(source_file):
    """
    Create the Y4M file, which will serve as the reference video data
    from which we will make our reference VP8 and VP9 streams.
    """
    y4m_start = ['ffmpeg', '-y', '-i', source_file]
    y4m_codec = t['formats']['y4m']['codec'].split(' ')
    y4m_opts = t['formats']['y4m']['options'].split(' ')
    y4m_out = c['y4m_sources'] + os.path.split(source_file)[1] + '.y4m'
    y4m_cmd = y4m_start + y4m_codec + y4m_opts + [y4m_out]
    print 'Converting source video stream to Y4M rawvideo container.'
    try:
        sp.check_output(y4m_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit('Error: Y4M rawvideo generation failed. Cannot continue.')
    finally:
        return True
