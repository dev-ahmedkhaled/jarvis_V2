from yapper import Yapper,GroqEnhancer,Persona,PiperSpeaker,PiperVoiceUS,PiperQuality
import pygame
from dotenv import load_dotenv
import os
def text_to_speech(text):
    load_dotenv()
    pygame.mixer.init()
    jarvis_api=os.getenv("tts_jarvis_API")

    speaker=PiperSpeaker.__new__(PiperSpeaker)
    speaker.onnx_f=os.getenv("jarvis_onnx_file")
    speaker.conf_f=os.getenv("jarvis_conf_file")
    speaker.exe_path=os.getenv("jarvis_piper_exe")
    tts=Yapper(speaker=speaker,enhancer=GroqEnhancer(api_key=jarvis_api,persona=Persona.JARVIS))
    tts.yap(text)



