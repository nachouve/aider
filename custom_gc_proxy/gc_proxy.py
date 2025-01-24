import os
import sys
from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import dotenv
import litellm

from colorama import Fore
from pprint import pprint
from copilot_completer.settings import Settings
from copilot_completer.github_auth import get_github_access_token
from copilot_completer.completer import get_copilot_token

litellm.set_verbose = True

env_locations = [".env", "aider/.env", "../.env", "../aider/.env", "../aider/aider/.env"]
for env_location in env_locations:
    if os.path.exists(env_location):
        dotenv.load_dotenv(env_location)
        break
if not os.getenv("GITHUB_COPILOT_ACCESS_TOKEN"):
    print(f"{Fore.RED}GITHUB_COPILOT_ACCESS_TOKEN not set{Fore.RESET}")

app = Flask(__name__)

MOCK_RESPONSE = True
LLM_PROVIDER_URL = os.getenv("LLM_PROVIDER_URL", "http://localhost:5000")

def copilot_login():
    gh_token = os.environ.get("GITHUB_COPILOT_ACCESS_TOKEN")
    settings = Settings.from_env()
    if gh_token is None:
        print("Need to login to GitHub Copilot. See instructions in the internet browser.")
        gh_token = get_github_access_token()
        print("TOKEN", gh_token)
        os.environ.setdefault("GITHUB_COPILOT_ACCESS_TOKEN", gh_token.access_token)
        settings.token = gh_token.access_token
    else:
        print("TOKEN", gh_token)
        settings.token = gh_token

def forward_request(endpoint, method='POST'):
    if MOCK_RESPONSE:
        print("****************************** Mocking response ******************************")
        return {
            "id": "mock-id",
            "choices": [
                {
                    "message": {
                        "content": "I'm doing great, how about you?"
                    }
                }
            ],
            "created": 1234567890,
            "model": "mock-model",
            "object": "chat.completion",
            "service_tier": "mock-service-tier",
            "system_fingerprint": "mock-system-fingerprint",
            "usage": {
                "completion_tokens": 10,
                "prompt_tokens": 10,
                "total_tokens": 20
            }
        }
    try:
        if method == 'POST':
            data = request.json
            resp = requests.post(f"{LLM_PROVIDER_URL}{endpoint}", json=data)
        elif method == 'GET':
            resp = requests.get(f"{LLM_PROVIDER_URL}{endpoint}")

        if resp.status_code == 200:
            return jsonify(resp.json()), 200
        else:
            return jsonify({"message": "Error forwarding request to LLM provider"}), resp.status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/chat_BORRAR/completions', methods=['POST'])
def chat_completions():
    print("DEBUG>>>> chat_completions")
    return forward_request('/chat/completions')

@app.route('/chat/completions', methods=['POST'])
def completions():
    url = "https://copilot-proxy.githubusercontent.com/v1/engines/copilot-codex/completions"
    kwargs = request.json
    required_params = ['model', 'temperature']
    missing_params = [param for param in required_params if param not in kwargs]
    if missing_params:
        raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    if not isinstance(kwargs['model'], str) or not kwargs['model'].strip():
        raise ValueError("The 'model' parameter must be a non-empty string.")

    copilot_login()

    print("DEBUG>>>> get_copilot_token()")
    COPILOT_TOKEN = get_copilot_token()
    print("DEBUG>>>> COPILOT_TOKEN", COPILOT_TOKEN)

    my_headers = {
        'OpenAI-Intent': 'conversation-panel',
        'OpenAI-Organization': 'github-copilot',
        'Authorization': f"Bearer {COPILOT_TOKEN}",
        'Content-Type': 'application/json',
        'user-agent': 'GitHubCopilotChat/0.23.2',
        'editor-version': 'vscode/1.89.1',
        'editor-plugin-version': 'copilot-chat/0.23.2',
        'openai-organization': 'github-copilot',
        'copilot-integration-id': 'vscode-chat',
        'vscode-machineid': 'ccc60edbc08ad1aac1be74576b329b10cdc2c094555f873711e3ca1a2e0f6afe'
    }

    data = {
        "messages": request.json.get("messages"),
        "model": request.json.get("model"), #"gpt-4o",
        "temperature": 0.1,
        "top_p": 1,
        "max_tokens": 4096,
        "n": 1,
        "stream": True
    }

    pprint(data)

    response = requests.post(url, headers=my_headers, json=data, stream=True, verify=False)

    print("Response received:", response.status_code)

    uve_count = [0]
    def generate():
        for line in response.iter_lines():
            if line:
                uve_count[0] += 1
                decoded_line = line.decode('utf-8')
                print(f"***************** uve_count: {uve_count[0]} *****************")
                aux_text = print_stream_response(decoded_line)
                print(f"[_{aux_text}_]")
                print(f"***************** uve_count: {uve_count[0]} *****************")
                yield f"{decoded_line}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def print_stream_response(response_text):
    import json
    kk_lines = response_text.split("\n")
    #print(Fore.BLUE, "Response_text decoded:", Fore.RESET, kk_lines)
    total_text = ""
    for l in kk_lines:
        pass
    for l in kk_lines:
        try:
            resp_json = json.loads(l.split("data: ")[1])
            curr_token = resp_json.get("choices")[0].get("delta").get("content")
            total_text += curr_token
        except:
            try:
                curr_token = resp_json.get("choices")[0].get("text")
                total_text += curr_token
            except:
                print(Fore.RED, "Error parsing response:", Fore.RESET, response_text, "\n", l)
    return total_text

@app.route('/models', methods=['GET'])
def models():
    return forward_request('/models', method='GET')

@app.route('/embeddings', methods=['POST'])
def embeddings():
    return forward_request('/embeddings')

if __name__ == "__main__":
    PORT = 4141 # AIAI
    DEBUG = False
    app.run(debug=DEBUG, port=PORT)
