import os
import sys

from flask import Flask, request, jsonify
import requests
import dotenv
import litellm
from colorama import Fore

litellm.set_verbose = True

env_locations = [".env", "aider/.env", "../.env", "../aider/.env", "../aider/aider/.env"]
for env_location in env_locations:
    if os.path.exists(env_location):
        dotenv.load_dotenv(env_location)
        break
if not os.getenv("GITHUB_COPILOT_ACCESS_TOKEN"):
    print(f"{Fore.RED}GITHUB_COPILOT_ACCESS_TOKEN not set{Fore.RESET}")
    sys.exit(1)


app = Flask(__name__)

MOCK_RESPONSE = True
# Assuming the LLM provider URL is set as an environment variable
LLM_PROVIDER_URL = os.getenv("LLM_PROVIDER_URL", "http://localhost:5000")

from copilot_completer.settings import Settings
from copilot_completer.github_auth import get_github_access_token
from copilot_completer.completer import get_copilot_token
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

    # Ensure 'model' parameter is a string and not empty
    if not isinstance(kwargs['model'], str) or not kwargs['model'].strip():
        raise ValueError("The 'model' parameter must be a non-empty string.")


    # Ensure 'max_tokens', 'temperature', and 'top_p' are of correct type and within expected ranges
    # if not isinstance(kwargs['max_tokens'], int) or kwargs['max_tokens'] <= 0:
    #     raise ValueError("The 'max_tokens' parameter must be a positive integer.")

    # if not isinstance(kwargs['temperature'], (int, float)) or not (0 <= kwargs['temperature'] <= 1):
    #     raise ValueError("The 'temperature' parameter must be a number between 0 and 1.")

    # if not isinstance(kwargs['top_p'], (int, float)) or not (0 <= kwargs['top_p'] <= 1):
    #     raise ValueError("The 'top_p' parameter must be a number between 0 and 1.")


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
            #'x-request-id': 'b36f22a9-88f0-47fc-bfb8-47bc6273adf6',
            #'x-github-api-version': '2023-07-07',
            'openai-organization': 'github-copilot',
            'copilot-integration-id': 'vscode-chat',
            #'vscode-sessionid': '204ccf01-6c28-42b0-8c8f-2d453199af051715499526505',
            'vscode-machineid': 'ccc60edbc08ad1aac1be74576b329b10cdc2c094555f873711e3ca1a2e0f6afe'
        }
    
    ## I got that values inspecting traffic of vscode with mitmproxy
    MODEL = "gpt-4o"
    kwargs = {
            'custom_llm_provider': MODEL.split("/")[0], 
            'model': f'"{MODEL}"',
            'n': 1,
            'temperature': 0.1,
            'max_tokens': 1024, # 4096
            #'intent': True,
            'top_p': 1,
            #'base_url': 'https://api.githubcopilot.com/chat/completions',
            #'api_base': 'https://api.githubcopilot.com/chat/completions',
            'base_url': url,
            'api_base': url,
            'headers': my_headers,
            # Added this stream: False
            'stream': "true",
        }

    OLD = False
    if OLD:
        print("litellm.completion()...")
        ## Just and nice example
        messages = [ 
                {
                    "content": "You are an AI programming assistant.\nWhen asked for your name, you must respond with \"GitHub Copilot\".\nFollow the user's requirements carefully & to the letter.\nFollow Microsoft content policies.\nAvoid content that violates copyrights.\nIf you are asked to generate content that is harmful, hateful, racist, sexist, lewd, violent, or completely irrelevant to software engineering, only respond with \"Sorry, I can't assist with that.\"\nKeep your answers short and impersonal.\nYou can answer general programming questions and perform the following tasks: \n* Ask a question about the files in your current workspace\n* Explain how the code in your active editor works\n* Review the selected code in your active editor\n* Generate unit tests for the selected code\n* Propose a fix for the problems in the selected code\n* Scaffold code for a new workspace\n* Create a new Jupyter Notebook\n* Find relevant code to your query\n* Propose a fix for the a test failure\n* Ask questions about VS Code\n* Generate query parameters for workspace search\n* Ask about VS Code extension development\n* Ask how to do something in the terminal\n* Explain what just happened in the terminal\nYou use the GPT-4 version of OpenAI's GPT models.\nFirst think step-by-step - describe your plan for what to build in pseudocode, written out in great detail.\nThen output the code in a single code block.\nMinimize any other prose.\nUse Markdown formatting in your answers.\nMake sure to include the programming language name at the start of the Markdown code blocks.\nAvoid wrapping the whole response in triple backticks.\nThe user works in an IDE called Visual Studio Code which has a concept for editors with open files, integrated unit test support, an output pane that shows the output of running the code as well as an integrated terminal.\nThe user is working on a Windows machine. Please respond with system specific commands if applicable.\nThe active document is the source code the user is looking at right now.\nYou can only give one reply for each conversation turn.\n",
                    "role": "system"
                },
                {
                    "content": "Tell me a 25 words joke of python programming",
                    "role": "user"
                },
            ]

        print(messages[-1])


        # kwargs.update({"messages": messages})
        # resp = litellm.completion(**kwargs)

        # # Parse the response from the custom API
        # if resp.status_code == 200:
        #     custom_api_data = resp.json()

        #     # Prepare the response according to the given instructions
        #     response_data = {
        #         'data': [
        #             {
        #                 'prompt': custom_api_data['data'][0]['prompt'],
        #                 'output': custom_api_data['data'][0]['output'],
        #                 'params': custom_api_data['data'][0]['params']
        #             }
        #         ],
        #         'message': 'ok'
        #     }
        #     return jsonify(response_data), 200
        # else:
        #     return jsonify({'message': f'Error communicating with the custom API. \n Response text:{resp.text}'}), resp.status_code
    else:
        url = "https://api.individual.githubcopilot.com/chat/completions"
        headers = {
            'authorization': f"Bearer {COPILOT_TOKEN}",
            'content-type': 'application/json',
            'copilot-integration-id': 'vscode-chat',
            'editor-plugin-version': 'copilot-chat/0.23.2',
            'editor-version': 'vscode/1.96.4',
            'openai-intent': 'conversation-panel',
            'openai-organization': 'github-copilot',
            'user-agent': 'GitHubCopilotChat/0.23.2',
            #'vscode-machineid': '<REDACTED_MACHINE_ID>',
            #'vscode-sessionid': '<REDACTED_SESSION_ID>',
            'x-github-api-version': '2024-12-15',
            #'x-request-id': '7162f088-6e73-46b9-9527-26ef612a1653',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-dest': 'empty',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=4, i'
        }

        test_data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI programming assistant.\nWhen asked for your name, you must respond with \"GitHub Copilot\".\nFollow the user's requirements carefully & to the letter.\nFollow Microsoft content policies.\nAvoid content that violates copyrights.\n"
                },
                {
                    "role": "user",
                    "content": "remove risky strings, personal passwords, etc."
                },
                {
                    "role": "user",
                    "content": "Tell me a 25 words joke of python programming"
                }
            ],
            "model": "gpt-4o",
            "temperature": 0.1,
            "top_p": 1,
            "max_tokens": 4096,
            "n": 1,
            "stream": True
        }

        data = {
            "messages": request.json.get("messages"),
            "model": "gpt-4o",
            "temperature": 0.1,
            "top_p": 1,
            "max_tokens": 4096,
            "n": 1,
            "stream": True
        }
    from pprint import pprint 
    
    pprint(data)
    
    import requests
    from flask import Response, stream_with_context
    response = requests.post(url, headers=headers, json=data, stream=True, verify=False)

    print("Response received:", response.status_code)

    uve_count = [0]
    def generate():
        for line in response.iter_lines():
            if line:
                uve_count[0] += 1
                print(f"***************** uve_count: {uve_count[0]} *****************")                
                aux_text = print_stream_response(line.decode('utf-8'))
                print(f"***************** uve_count: {uve_count[0]} *****************")
                yield f"{line.decode('utf-8')}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def print_stream_response(response_text):
    import json
    kk_lines = response_text.split("\n")
    total_text = ""
    for l in kk_lines:
        #print(l)
        pass
    for l in kk_lines:
        try:
            curr_token = json.loads(l[6:]).get("choices")[0].get("delta").get("content")
            print(curr_token)
            total_text += curr_token
        except:
            pass
    return total_text

@app.route('/models', methods=['GET'])
def models():
    return forward_request('/models', method='GET')

@app.route('/embeddings', methods=['POST'])
def embeddings():
    return forward_request('/embeddings')

if __name__ == "__main__":
    app.run(debug=True)

def print_stream_response(response):
    import json
    kk_lines = response.text.split("\n")
    for l in kk_lines:
        print(l)
    for l in kk_lines:
        try:
            l2 = json.loads(l[6:]).get("choices")[0].get("delta").get("content")
            print(l2)
        except:
            pass


@app.route('/models', methods=['GET'])
def models():
    return forward_request('/models', method='GET')

@app.route('/embeddings', methods=['POST'])
def embeddings():
    return forward_request('/embeddings')

if __name__ == "__main__":
    app.run(debug=True)
