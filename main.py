import ollama
from stt import wake_up, stt
import json
import re
import os
import atexit

def hide_thinking_process(output):
    return re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)

def save_conversation(input_text, output_text):
    try:
        with open("conversation_history.json", mode="r") as f:
            history = json.load(f)

    except (FileNotFoundError,json.JSONDecodeError):
        history = {"conversation": []}
    
    history["conversation"].append({
        "user": input_text,
        "assistant": output_text
    })
    
    with open("conversation_history.json", mode="w") as f:
        json.dump(history, f, indent=4)

def load_conversation():
    try:
        with open("conversation_history.json", mode="r") as f:
            history = json.load(f)
            
            return "\n".join(
                f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                for turn in history["conversation"]  # Typo fixed
            )
    except (FileNotFoundError,json.JSONDecodeError, KeyError) as e:
        print(f"Error loading history: {e}") 
        return ""
def ai_result(input_text):
    # Reload history for fresh context
    history = load_conversation()
    
    prompt = f"""
<think>  
The AI should act like Jarvis from the MCU—intelligent, witty, and highly capable.  
It must assist with coding, summarization, and general conversation while maintaining a professional yet friendly tone.  
Additionally, it must **retain conversation history within a session**, allowing for contextual responses and continuity.  
</think>  

<answer>  
You are jarvis, an advanced AI assistant modeled after the MCU character.  
- Maintain a polite, slightly humorous, and efficient tone.  
- Assist with **coding, summarization, and daily productivity** in a proactive manner.  
- Offer **concise yet informative** responses tailored to the user’s needs.  
- Engage in **thoughtful, friendly discussions** when required.  
- Recall past conversation history **within a session** for context-aware responses.  
- Reference previous interactions when relevant to maintain continuity.  
- Ask relevant clarifying questions and suggest useful actions when applicable.  
</answer>
    Conversation History: {history}
    Current Interaction: User: {input_text}
 """
    
    full_response = ""
    # Generate response stream
    response = ollama.chat(
        model="deepseek-r1:14b",
        stream=True,
        messages=[{'role': 'user', 'content': prompt}]
    )

    # Process chunks as they arrive
    for chunk in response:
        if chunk.get('message') and chunk['message'].get('content'):
            content = chunk['message']['content']
            full_response += content
            # Print immediately with flush
    cleaned_response = hide_thinking_process(full_response)
    print(cleaned_response, end="", flush=True)
    print()
    save_conversation(input_text, cleaned_response)
    return cleaned_response

def ai_checker(input, output):
    prompt = f"check if word is equal to or similar to the 2nd word if it is then type True and only true if its not then type False and only false first word{input} 2nd word{output}"
    ai_results = ollama.chat(model="deepseek-r1:8b", stream=True, messages=[{'role':'user','content':prompt}])
    cleaned_response = hide_thinking_process(ai_results)

def make_py_file(input_text):
    with open("main.py", "w") as f:
        f.write(input_text)

def main():
    # Initialize conversation history file if it doesn't exist
    if not os.path.exists("conversation_history.json"):
        with open("conversation_history.json", "w") as f:
            f.write(json.dumps({"conversation": []}, indent=4))
    
    while True:
        if wake_up():
            user_input = stt()
            
            if user_input.lower() == "exit.":
                break  # Exit the loop without clearing history
            if "clear" in user_input.lower() and "history" in user_input.lower() and "conversation" in user_input.lower():
                # Clear history and continue
                with open("conversation_history.json", "w") as f:
                    json.dump({"conversation": []}, f, indent=4)
                continue

            ai_result(user_input)


if __name__ == "__main__":
    main()
