from RealtimeSTT import AudioToTextRecorder
import pvporcupine
import os
import pyaudio
import struct
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def async_stt_main():
    loop = asyncio.get_running_loop()
    def sync_record():
        with AudioToTextRecorder(model="medium", device="cuda", 
                               compute_type="float32", language="en") as recorder:
            return recorder.text()
    return await loop.run_in_executor(None, sync_record)

async def async_wake_up():
    access_key = os.getenv('wake_up_key')
    porcupine = pvporcupine.create(keywords=["jarvis"], access_key=access_key)
    pa = pyaudio.PyAudio()
    
    detection_event = asyncio.Event()
    loop = asyncio.get_running_loop()  # Get the running event loop

    def audio_callback(in_data, frame_count, time_info, status):
        """PyAudio callback that checks for wake word"""
        try:
            pcm = struct.unpack_from("h" * porcupine.frame_length, in_data)
            if porcupine.process(pcm) >= 0:
                loop.call_soon_threadsafe(detection_event.set)
        except Exception as e:
            print(f"Audio callback error: {e}")
        return (in_data, pyaudio.paContinue)
    
    # Initialize audio stream with proper async handling
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        stream_callback=audio_callback,  # No need for lambda, directly pass the function
        start=False
    )
    
    print("Listening for wake word 'Jarvis'...")
    stream.start_stream()
    
    try:
        await detection_event.wait()
        print("Wake word detected!")
        return True
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()