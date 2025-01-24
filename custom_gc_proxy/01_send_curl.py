import requests
import json
import colorama
from colorama import Fore
from pprint import pprint

colorama.init()

API_URL = "http://localhost:5000/chat/completions"
DEBUG = False

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

data = {
    "model": "curl",
    "temperature": 0.9,
    "messages": [
        {
            "role": "user",
            "content": "Tell me a joke with mixture Python programming and veganism"
        }
    ]
}

def process_sse_response(response):
    """
    Process the SSE response and extract the content from choices[0].delta.content.

    Args:
        response (dict): The SSE response.

    Returns:
        str: The extracted content.
    """
    try:
        content = response.get("choices")[0].get("delta").get("content")
        return content
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