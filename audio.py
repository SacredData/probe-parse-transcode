import os
import sys
import subprocess as sp
import yaml

cfile = open('probe/config.yaml', 'r')
cconfig = yaml.load_all(cfile)
for datac in cconfig:
    c = datac


def build_wav(source_video):
    wav_out = c['wav_sources'] + os.path.split(source_video)[1] + '.wav'
    try:
        wav_cmd = ['ffmpeg', '-y', '-i', source_video, '-vn', '-sn', '-map',
                   '0:a', wav_out]
        sp.check_output(wav_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit("Error: WAV audio extraction")
    finally:
        return wav_out


def build_ogg(source_wav):
    ogg_out = c['ogg_sources'] + os.path.split(source_wav)[1] + '.ogg'
    try:
        ogg_cmd = ['oggenc', source_wav, '-o', ogg_out]
        sp.check_output(ogg_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit("Error: OGG audio conversion")
    finally:
        return ogg_out


def build_opus(source_wav):
    opus_out = c['opus_sources'] + os.path.split(source_wav)[1] + '.opus'
    try:
        opus_cmd = ['opusenc', '--bitrate', '160', source_wav, opus_out]
        sp.check_output(opus_cmd, stderr=sp.STDOUT)
    except sp.SubprocessError:
        sys.exit("Error: OPUS audio conversion")
    finally:
        return opus_out
