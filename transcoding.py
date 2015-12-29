import json
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
        return y4m_out


def build_vp9(y4m):
    """
    This method will convert a Y4M (4:2:0 colorspace) raw video stream
    into a reference-level VP8/VP9 video stream contained within a
    WebM file. The target argument must be an array: [target_bit_rate,
    multi_webm_start]. Provide this data as [int, str], respectively.
    """
    y4m_file = os.path.split(y4m)[1]
    vp_opts = t['formats']['vp9']['vpxenc'].split(' ')
    vp_out = c['vp9_sources'] + os.path.split(y4m)[1] + '.vp9'
    if y4m_file.endswith('.y4m'):
        analysis_data = c['analysis_logs_dir'] + y4m_file[:-4] + '.data'
    else:
        sys.exit('Error! No analysis file found. Cannot set targets.')
    with open(analysis_data, 'r') as f:
        read_data = f.read()
    jdata = json.loads(read_data)
    stm_data = jdata['streams']
    for stream in stm_data:
        if stream['codec_type'] in 'video':
            video_stream = stream
            print 'Found video stream in the file.'
    mbps = int(video_stream["bit_rate"]) / 1000000
    vp_bits = '--target-bitrate=' + str(mbps)
    vp_args = [vp_bits, '-o', vp_out, y4m]
    vp_cmd = vp_opts + vp_args
    try:
        sp.check_output(vp_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit('Error: VP9 conversion.')
    return vp_out


def build_webm(vp_source):
    vp_file = os.path.split(vp_source)[1]
    webm_out = c['webm_sources'] + vp_file + '.webm'
    audio_stream = c['opus_sources'] + vp_file[:-13] + '.wav.opus'
    print audio_stream
    if os.path.isfile(audio_stream):
        print 'Found audio stream'
    else:
        print 'No audio stream found'
    return webm_out
