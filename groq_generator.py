import json
import os
from typing import Dict, Any
import groq
import curses

def generate_levels(api_key: str, num_levels: int) -> Dict[str, Any]:
    client = groq.Client(api_key=api_key)
    system_prompt = '''Generate JSON with ascending levels of difficulty based on the provided number > 10. 
Each level should follow this exact structure:

{
    "levelX": {
        "bush1": {
            "instructions": "Task description",
            "pre_code": "Python code here",
            "expected_output": "Expected result"
        },
        "bush2": { ... },
        "bush3": { ... },
        "bush4": { ... },
        "bush5": { ... }
    }
}

Where X is the level number (11 and up). Each bush should contain a programming task of increasing difficulty.
The pre_code should be valid Python code that students need to complete.
The expected_output should be the exact string output expected from the code.'''
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Generate {num_levels} complete levels starting from level 11, following the exact JSON structure shown. Each level should be more difficult than the last."
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=32768
        )
        
        # Extract and parse the JSON from the response
        response_text = completion.choices[0].message.content
        # Find the JSON content between ``` markers if present
        if "```json" in response_text:
            json_content = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_content = response_text.split("```")[1].split("```")[0]
        else:
            json_content = response_text
            
        new_levels = json.loads(json_content)
        
        # Save to temporary file
        with open('temp_levels.json', 'w') as f:
            json.dump(new_levels, f, indent=4)
            
        return new_levels
        
    except Exception as e:
        print(f"Error generating levels: {e}")
        return {}

def merge_levels(existing_levels: Dict[str, Any], new_levels: Dict[str, Any]) -> Dict[str, Any]:
    """Merge new levels with existing levels."""
    merged = existing_levels.copy()
    merged.update(new_levels)
    return merged

def get_groq_api_key(stdscr) -> str:
    """Get Groq API key from user input."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    prompt = "Enter your Groq API key: "
    stdscr.addstr(h//2, w//2 - len(prompt)//2, prompt)
    curses.echo()
    curses.curs_set(1)
    api_key = ""
    
    while True:
        try:
            y = h//2
            x = w//2 - len(prompt)//2 + len(prompt)
            stdscr.addstr(y, x, " " * 50)  # Clear previous input
            stdscr.addstr(y, x, api_key)
            char = stdscr.getch()
            if char == ord('\n'):
                break
            elif char == ord('\b') or char == 127:  # Backspace
                api_key = api_key[:-1]
            else:
                api_key += chr(char)
        except curses.error:
            pass
    
    curses.noecho()
    curses.curs_set(0)
    return api_key.strip()
