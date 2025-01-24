import requests
import json
import colorama
from colorama import Fore
from pprint import pprint

colorama.init()

API_URL = "http://localhost:4141/chat/completions"
DEBUG = False

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

data = {
    "model": "curl",
    "temperature": 0.1,
    "messages": [
        {
            "role": "user",
            "content": "Tell me a joke about Python programming and AI in 10 words."
        }
    ]
}

def process_sse_response(response):
    """
    Process the SSE response and extract the content from:
        - choices[0].delta.content, or
        - choices[0].text

    Args:
        response (dict): The SSE response.

    Returns:
        str: The extracted content.
    """
    try:
        choices = response.get("choices", [])
        if not choices:
            return None
        delta = choices[0].get("delta", {})
        if "content" in delta:
            return delta["content"]
        if "text" in choices[0]:
            return choices[0]["text"]
        return None
    except (AttributeError, IndexError, TypeError):
        return None

print(Fore.YELLOW)
print("-"*100)
print(f"Request to API: {API_URL}")
print("Data:")
pprint(data)
print("-"*100)
print(Fore.RESET)

response = requests.post(API_URL, headers=headers, data=json.dumps(data), stream=True)

print(Fore.GREEN)
print("-"*100)
print("Response:", Fore.RESET)

# Process the SSE response line by line
for line in response.iter_lines():
    if line:
        try:
            line = line.decode('utf-8').strip()
            if line.startswith("data: "):
                line = line[len("data: "):]
            if DEBUG: print(Fore.CYAN, f"Received line: {line}", Fore.RESET)
            event = json.loads(line)
            content = process_sse_response(event)
            if content:
                print(content, end="")
        except json.JSONDecodeError as e:
            print(Fore.RED, f"JSON Decode Error: {e}", Fore.RESET)
            continue
        except Exception as e:
            print(Fore.RED, f"Unexpected Error: {e}", Fore.RESET)
            continue

print(Fore.GREEN)
print("-"*100, Fore.RESET)