from RealtimeSTT import AudioToTextRecorder
import pvporcupine
import os
import pyaudio
import struct
from dotenv import load_dotenv
import time
import threading

load_dotenv()

def stt():
    with AudioToTextRecorder(model="tiny", device="cuda", 
                             compute_type="float32", language="en") as recorder:
        return recorder.text()
def wake_up():
    access_key = os.getenv('wake_up_key')
    porcupine = pvporcupine.create(keywords=["jarvis"], access_key=access_key)
    pa = pyaudio.PyAudio()
    wake_word_detected = False

    def audio_callback(in_data, frame_count, time_info, status):
        """PyAudio callback that checks for wake word"""
        nonlocal wake_word_detected
        try:
            pcm = struct.unpack_from("h" * porcupine.frame_length, in_data)
            if porcupine.process(pcm) >= 0:
                print("Wake word detected!")
                wake_word_detected = True
                return (in_data, pyaudio.paComplete)
        except Exception as e:
            print(f"Audio callback error: {e}")
        return (in_data, pyaudio.paContinue)

    # Initialize audio stream
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        stream_callback=audio_callback,
        start=False
    )

    print("Listening for wake word 'Jarvis'...")
    stream.start_stream()

    try:
        while stream.is_active():
            if wake_word_detected:
                break
            time.sleep(0.1)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

    return wake_word_detected
