import requests
from requests.exceptions import RequestException
from colorama import Fore, Style, init
import json
import time
import threading
import argparse
import signal
import sys
from rich.console import Console
from rich.table import Table

init(autoreset=True)
console = Console()

def check_ollama_status():
    try:
        response = requests.get("http://localhost:11434/")
        if response.status_code == 200 and "ollama is running" in response.text.lower():
            print(Fore.GREEN + "Ollama is running.")
            return True
        else:
            print(Fore.RED + "Ollama is not running.")
            return False
    except RequestException as e:
        print(Fore.RED + f"Error checking Ollama status: {str(e)}")
        return False

def list_models():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get("models", [])
            table = Table(title="Available Models")
            table.add_column("Name", style="cyan")
            table.add_column("Modified At", style="magenta")
            table.add_column("Size", style="green")
            table.add_column("Digest", style="yellow")
            table.add_column("Details", style="blue")

            for model in models:
                details = model.get("details", {})
                details_str = f"Format: {details.get('format')}, Family: {details.get('family')}, Parameter Size: {details.get('parameter_size')}, Quantization Level: {details.get('quantization_level')}"
                table.add_row(
                    model["name"],
                    model["modified_at"],
                    str(model["size"]),
                    model["digest"],
                    details_str
                )
            console.print(table)
        else:
            print(Fore.RED + f"Failed to get models. Status code: {response.status_code}")
            print(Fore.RED + f"Response text: {response.text}")
    except RequestException as e:
        print(Fore.RED + f"Error occurred: {str(e)}")

def ollama_completion(prompt, model, temperature, max_tokens):
    if not check_ollama_status():
        return {"error": "Ollama is not running"}

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(Fore.GREEN + "Sending request to Ollama completion API...")

    def visual_counter():
        start_time = time.time()
        while not stop_event.is_set():
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            print(Fore.YELLOW + f"\rElapsed time: {int(minutes)}m {int(seconds)}s", end="")
            time.sleep(1)
        print(Fore.YELLOW + f"\rTotal time: {int(minutes)}m {int(seconds)}s")

    def signal_handler(sig, frame):
        print(Fore.RED + "\nRequest cancelled by user.")
        stop_event.set()
        counter_thread.join()  # Ensure the counter thread is joined before exiting
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    stop_event = threading.Event()
    counter_thread = threading.Thread(target=visual_counter)
    counter_thread.start()

    try:
        response = requests.post(url, json=payload, headers=headers)
        stop_event.set()
        counter_thread.join()
        print(Fore.BLUE + "Request sent. Awaiting response...")
        if response.status_code == 200:
            print(Fore.GREEN + "Response received successfully.")
            return response
        elif response.status_code == 404:
            print(Fore.RED + "Endpoint not found. Please check the URL.")
            return {"error": "Endpoint not found"}
        else:
            print(Fore.RED + f"Failed to get completion. Status code: {response.status_code}")
            print(Fore.RED + f"Response text: {response.text}")
            return {"error": "Failed to get completion"}
    except RequestException as e:
        stop_event.set()
        counter_thread.join()
        print(Fore.RED + f"Error occurred: {str(e)}")
        return {"error": str(e)}

def process_ollama_response(response_lines):
    complete_response = ""
    for line in response_lines:
        response_data = json.loads(line)
        complete_response += response_data["response"]
        if response_data.get("done"):
            break
    return complete_response

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call Ollama completion API")
    parser.add_argument("--model", type=str, default="llama2:latest", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature")
    parser.add_argument("--max_tokens", type=int, default=100, help="Max tokens")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--message", type=str, help="Prompt message")
    args = parser.parse_args()

    if args.list:
        list_models()
    else:
        if args.message:
            prompt = args.message
        else:
            prompt = input("Soy un robot. Dime algo: ")
        prompt = "Be concise. " + prompt
        print(Fore.MAGENTA + "PROMPT: " + prompt)
        result = ollama_completion(prompt, args.model, args.temperature, args.max_tokens)
        if "error" not in result:
            response_lines = result.text.splitlines()
            final_response = process_ollama_response(response_lines)
            print(Fore.CYAN + "Final Response:")
            print(final_response)
        else:
            print(Fore.RED + "Error:")
            print(result)
