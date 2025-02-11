
from RealtimeSTT import AudioToTextRecorder  
from googletrans import Translator


def main():
    # Initialize the real-time speech-to-text recognizer
    with AudioToTextRecorder(model="medium", device="cuda", compute_type="float32") as recorder:
            try:
                # Retrieve text from the audio recorder
                recorded_text = recorder.text()
                print(f"Recorder Output: {recorded_text}")
            except Exception as e:
                print(f"Error with AudioToTextRecorder: {e}")




if __name__ == "__main__":
    main()





