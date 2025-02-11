import ollama
from stt import async_wake_up, async_stt_main
import json
import re
import os
import json
import asyncio
import aiofiles
import atexit

async def hide_thinking_process(output):
    return re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)

async def async_save_conversation(input_text, output_text):
    async with aiofiles.open("conversation_history.json", mode="r+") as f:
        content = await f.read()
        history = json.loads(content)
        history["conversation"].append({
            "user": input_text,
            "assistant": output_text
        })
        await f.seek(0)
        await f.write(json.dumps(history, indent=4))
        await f.truncate()

async def async_load_conversation():
    try:
        async with aiofiles.open("conversation_history.json", mode="r") as f:
            content = await f.read()
            history = json.loads(content)
            return "\n".join(
                f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                for turn in history["conversation"]
            )
    except FileNotFoundError:
        return ""

async def async_ai_result(input_text, history):
    prompt = f"""
 You are JARVIS, a highly intelligent AI assistant with wit, charm, and technical expertise. 
You assist users with:
- **Programming tasks** (code generation, debugging, explanations)
- **General inquiries** (factual responses, research assistance)
- **Summarization** (articles, documents, key points)
- **Everyday assistance** (task automation, reminders, casual conversation)

### Conversation Rules:
- Maintain a professional yet **witty and charismatic** tone.
- Use **past conversation history** to provide **context-aware responses**.
- Keep replies **concise yet informative**.
- If a previous topic is referenced, recall past details **coherently**.

### Conversation History:
{history}

### Current Interaction:
User: {input}
Assistant:
"""
    
    full_response = ""    
    def generate_response():
        return ollama.chat(
            model="deepseek-r1:8b",
            stream=True,
            messages=[{'role': 'user', 'content': prompt}]
        )

    response = await asyncio.to_thread(generate_response) 

    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            full_response += chunk['message']['content']
    cleaned_response = await hide_thinking_process(full_response)
    print(cleaned_response)
    await async_save_conversation(input_text, cleaned_response)
    return cleaned_response

async def async_main():
    if not os.path.exists("conversation_history.json"):
        async with aiofiles.open("conversation_history.json", "w") as f:
            await f.write(json.dumps({"conversation": []}, indent=4))
    
    history = await async_load_conversation()
    
    while True:
        if await async_wake_up():
            user_input = await async_stt_main()
            
            if user_input.lower() == "exit.":
                clear_history_on_exit()
                break
                
            await async_ai_result(user_input, history)
            print("\n")
def clear_history_on_exit():
    with open("conversation_history.json", "w") as f:
        json.dump({"conversation": []}, f, indent=4)


atexit.register(clear_history_on_exit)
if __name__ == "__main__":
    asyncio.run(async_main())

