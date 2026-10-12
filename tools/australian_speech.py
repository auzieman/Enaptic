#!/usr/bin/python3
"""Small local ONNX voice trial. GPL-3.0-or-later.
Model: DataCraftsmanAustralia/en_AU-librivox-medium (CC BY 4.0).
Voice lineage: Jenny (Dioco); selected narrator: magdalena / Kirra.
Uses the public eSpeak phoneme API and the model's own token map.
"""
import argparse
import ctypes as c
import json
from pathlib import Path
import sys
import time
import tempfile
import subprocess
import wave

VOICES={'bindi':1,'marlo':2,'kirra':3,'matilda':7,'tully':8,'willow':9}

def synthesize(text,model,output,voice='kirra'):
    import numpy as np
    import onnxruntime as ort
    config=json.loads(Path(str(model)+'.json').read_text());mapping=config['phoneme_id_map']
    espeak=c.CDLL('libespeak-ng.so.1');espeak.espeak_Initialize.argtypes=[c.c_int,c.c_int,c.c_char_p,c.c_int];espeak.espeak_SetVoiceByName.argtypes=[c.c_char_p];espeak.espeak_TextToPhonemes.argtypes=[c.POINTER(c.c_void_p),c.c_int,c.c_int];espeak.espeak_TextToPhonemes.restype=c.c_char_p
    if espeak.espeak_Initialize(2,0,None,0)<0:raise RuntimeError('Could not initialize eSpeak phonemizer')
    if espeak.espeak_SetVoiceByName(config['espeak']['voice'].encode()):raise RuntimeError('Required phonemizer voice unavailable')
    data=c.create_string_buffer(text.encode());pointer=c.c_void_p(c.addressof(data));sentences=[]
    while pointer.value:
        previous=pointer.value;value=espeak.espeak_TextToPhonemes(c.byref(pointer),1,2)
        if value:
            phones=value.decode().strip()
            if phones:sentences.append(phones)
        if pointer.value==previous:break
    espeak.espeak_Terminate()
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    session=ort.InferenceSession(str(model),sess_options=options,providers=['CPUExecutionProvider'])
    inference=config['inference'];scales=np.array([inference['noise_scale'],1.25 if voice=='tully' else 1.08 if voice=='marlo' else inference['length_scale'],inference['noise_w']],dtype=np.float32)
    chunks=[];start=time.monotonic()
    for phones in sentences:
        ids=list(mapping['^'])+list(mapping['_'])
        for phone in phones:
            if phone not in mapping:raise RuntimeError('Unsupported phoneme '+repr(phone)+'; this voice trial needs a full Piper frontend for this text')
            ids+=mapping[phone]+mapping['_']
        ids+=mapping['$']
        feed={'input':np.asarray([ids],dtype=np.int64),'input_lengths':np.asarray([len(ids)],dtype=np.int64),'scales':scales,'sid':np.asarray([VOICES[voice]],dtype=np.int64)}
        audio=session.run(None,feed)[0].reshape(-1)
        chunks.append(np.clip(audio*32767,-32767,32767).astype('<i2'))
        chunks.append(np.zeros(int(config['audio']['sample_rate']*.15),dtype='<i2'))
    if not chunks:raise ValueError('No speech generated')
    audio=np.concatenate(chunks)
    with wave.open(str(output),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(config['audio']['sample_rate']);f.writeframes(audio.tobytes())
    return dict(seconds=len(audio)/config['audio']['sample_rate'],inference_seconds=time.monotonic()-start,voice=voice)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('text');parser.add_argument('--model',type=Path,default=Path.home()/'.local/share/alpine-speech/en_AU-librivox-medium.onnx');parser.add_argument('--output',type=Path);parser.add_argument('--voice',choices=VOICES,default='kirra');args=parser.parse_args()
    print('Australian LibriVox voice by Data Craftsman; base voice attribution: Jenny (Dioco).',file=sys.stderr)
    temporary=args.output is None
    if temporary:
        fd,path=tempfile.mkstemp(prefix='alpine-speech-',suffix='.wav');__import__('os').close(fd);args.output=Path(path)
    try:
        print(json.dumps(synthesize(args.text,args.model,args.output,args.voice)))
        if temporary:subprocess.run(['paplay',str(args.output)],check=True)
    finally:
        if temporary:args.output.unlink(missing_ok=True)
if __name__=='__main__':main()
