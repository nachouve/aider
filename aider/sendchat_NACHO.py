import hashlib
import json

import backoff
import httpx
import openai

from aider.dump import dump  # noqa: F401
from aider.litellm import litellm

# from diskcache import Cache


CACHE_PATH = "~/.aider.send.cache.v1"
CACHE = None
# CACHE = Cache(CACHE_PATH)

import os
proxies = {
    "http": os.getenv('HTTP_PROXY'),
    "https": os.getenv('HTTPS_PROXY'),
}

def should_giveup(e):
    if not hasattr(e, "status_code"):
        return False

    return not litellm._should_retry(e.status_code)


@backoff.on_exception(
    backoff.expo,
    (
        httpx.ConnectError,
        httpx.RemoteProtocolError,
        litellm.exceptions.APIConnectionError,
        litellm.exceptions.APIError,
        litellm.exceptions.RateLimitError,
        litellm.exceptions.ServiceUnavailableError,
        litellm.exceptions.Timeout,
    ),
    giveup=should_giveup,
    max_time=60,
    on_backoff=lambda details: print(
        f"{details.get('exception','Exception')}\nRetry in {details['wait']:.1f} seconds."
    ),
)
def send_with_retries(model_name, messages, functions, stream):
    import ipdb
    kwargs = dict(
        model=model_name,
        messages=messages,
        temperature=0,
        stream=stream,
    )
    if functions is not None:
        kwargs["functions"] = functions

    key = json.dumps(kwargs, sort_keys=True).encode()

    # Generate SHA1 hash of kwargs and append it to chat_completion_call_hashes
    hash_object = hashlib.sha1(key)

    if not stream and CACHE is not None and key in CACHE:
        return hash_object, CACHE[key]

    # del kwargs['stream']

    ## NachoV Notes:
    ## TODO: Check what is sended
    ## TODO: Check if that can be interpreted by github copilot
    
    USE_PERSONAL_COMPLETION_SYSTEM_LITELLM_MY_CUSTOM = False
    USE_PERSONAL_COMPLETION_SYSTEM_REQUEST = True

    if USE_PERSONAL_COMPLETION_SYSTEM_LITELLM_MY_CUSTOM:

        ipdb.set_trace()
        import os
        from copilot_completer.settings import Settings
        from copilot_completer.github_auth import get_github_access_token
        from copilot_completer.completer import get_copilot_token

        
        def my_get_token() -> str:
            if env_token := os.environ.get("GITHUB_COPILOT_ACCESS_TOKEN", ""):
                return env_token
            else:
                print("Not found GITHUB_COPILOT_ACCESS_TOKEN")
                return ""

        gh_token = os.environ.get("GITHUB_COPILOT_ACCESS_TOKEN", None) 
        settings = Settings.from_env()
        if gh_token is None:
            gh_token = get_github_access_token()
            print("TOKEN", gh_token)
            os.environ.setdefault("GITHUB_COPILOT_ACCESS_TOKEN", gh_token.access_token)
            settings.token = gh_token.access_token
        else:
            settings.token = gh_token

        plain_message = ""
        for msg in kwargs.get("messages"):
            role = msg.get('role', 'unknown')  # get role, default to 'unknown' if not found
            content = msg.get('content', '')  
            plain_message += f"{role}: {content}"
        print("*"*50)
        print(plain_message)
        print("*"*50)
        my_headers = {
            'OpenAI-Intent': 'conversation-panel',
            'OpenAI-Organization': 'github-copilot',
            'Authorization': f"Bearer {get_copilot_token()}",
            'Content-Type': 'application/json',
            'user-agent': 'GitHubCopilotChat/0.15.1',
            'editor-version': 'vscode/1.89.1',
            'editor-plugin-version': 'copilot-chat/0.15.1',
            #'x-request-id': 'b36f22a9-88f0-47fc-bfb8-47bc6273adf6',
            #'x-github-api-version': '2023-07-07',
            'openai-organization': 'github-copilot',
            'copilot-integration-id': 'vscode-chat',
            #'vscode-sessionid': '204ccf01-6c28-42b0-8c8f-2d453199af051715499526505',
            'vscode-machineid': 'ccc60edbc08ad1aac1be74576b329b10cdc2c094555f873711e3ca1a2e0f6afe'
        }
        ## I got that values inspecting traffic of vscode with mitmproxy
        MODEL = f"my_custom/{model_name}"
        print(f"MODEL: {MODEL}")
        ipdb.set_trace()
        kwargs.update({
            'custom_llm_provider': 'my_custom', # 'github-copilot
            'model': MODEL,
            'n': 1,
            'temperature': 0.1,
            'max_tokens': 2540,
            #'intent': True,
            'top_p': 1,
            'base_url': 'https://api.githubcopilot.com/chat/completions',
            'api_base': 'https://api.githubcopilot.com/chat/completions',
            'headers': my_headers,            
        })
        from pprint import pprint
        pprint(kwargs)
        ipdb.set_trace()
        res = litellm.completion(**kwargs)
        # res is a generator that returns res
        res = [res]  
    elif USE_PERSONAL_COMPLETION_SYSTEM_REQUEST:
        print(f"SELECTED!!!! USE_PERSONAL_COMPLETION_SYSTEM_REQUEST")
        import ipdb
        ipdb.set_trace()
        res = custom_completation_requests_call(kwargs)
    else:
        ### Try do it like originally
        import ipdb
        ipdb.set_trace()
        res = litellm.completion(**kwargs)

    if not stream and CACHE is not None:
        CACHE[key] = res

    ipdb.set_trace()
    return hash_object, res 

def custom_completation_requests_call(kwargs):
    """
    NachoV Custom completation call.

    It must get a generator that returns ModelResponse
    """
    import ipdb

    ipdb.set_trace()
    import os
    from copilot_completer.settings import Settings
    from copilot_completer.github_auth import get_github_access_token
    from copilot_completer.completer import get_copilot_token
        
    import requests
    from colorama import Fore


    gh_token = os.environ.get("GITHUB_COPILOT_ACCESS_TOKEN", None) 
    settings = Settings.from_env()
    if gh_token is None:
        gh_token = get_github_access_token()
        print("TOKEN", gh_token)
        os.environ.setdefault("GITHUB_COPILOT_ACCESS_TOKEN", gh_token.access_token)
        settings.token = gh_token.access_token
    else:
        settings.token = gh_token


    url = "https://api.githubcopilot.com/chat/completions"

    headers = {
        "OpenAI-Intent": "conversation-panel",
        "OpenAI-Organization": "github-copilot",
        "Authorization": f"Bearer {get_copilot_token()}",
        "Content-Type": "application/json",
        "user-agent": "GitHubCopilotChat/0.15.1",
        "editor-version": "vscode/1.89.1",
        "editor-plugin-version": "copilot-chat/0.15.1",
        "x-request-id": "b36f22a9-88f0-47fc-bfb8-47bc6273adf6",
        "x-github-api-version": "2023-07-07",
        "openai-organization": "github-copilot",
        "copilot-integration-id": "vscode-chat",
        "vscode-sessionid": "204ccf01-6c28-42b0-8c8f-2d453199af051715499526505",
        "vscode-machineid": "ccc60edbc08ad1aac1be74576b329b10cdc2c094555f873711e3ca1a2e0f6afe",
    }

    ## Just and nice example
    aux_messages = [ 
            {
                "content": "You are an AI programming assistant.\nWhen asked for your name, you must respond with \"GitHub Copilot\".\nFollow the user's requirements carefully & to the letter.\nFollow Microsoft content policies.\nAvoid content that violates copyrights.\nIf you are asked to generate content that is harmful, hateful, racist, sexist, lewd, violent, or completely irrelevant to software engineering, only respond with \"Sorry, I can't assist with that.\"\nKeep your answers short and impersonal.\nYou can answer general programming questions and perform the following tasks: \n* Ask a question about the files in your current workspace\n* Explain how the code in your active editor works\n* Review the selected code in your active editor\n* Generate unit tests for the selected code\n* Propose a fix for the problems in the selected code\n* Scaffold code for a new workspace\n* Create a new Jupyter Notebook\n* Find relevant code to your query\n* Propose a fix for the a test failure\n* Ask questions about VS Code\n* Generate query parameters for workspace search\n* Ask about VS Code extension development\n* Ask how to do something in the terminal\n* Explain what just happened in the terminal\nYou use the GPT-4 version of OpenAI's GPT models.\nFirst think step-by-step - describe your plan for what to build in pseudocode, written out in great detail.\nThen output the code in a single code block.\nMinimize any other prose.\nUse Markdown formatting in your answers.\nMake sure to include the programming language name at the start of the Markdown code blocks.\nAvoid wrapping the whole response in triple backticks.\nThe user works in an IDE called Visual Studio Code which has a concept for editors with open files, integrated unit test support, an output pane that shows the output of running the code as well as an integrated terminal.\nThe user is working on a Windows machine. Please respond with system specific commands if applicable.\nThe active document is the source code the user is looking at right now.\nYou can only give one reply for each conversation turn.\n",
                "role": "system"
            },
            {
                "content": "Help me ",
                "role": "user"
            },
        ]

    messages = kwargs.get("messages") + [{"role": "user", "content": "Help me with what I've asked for."}]
    print(messages[-1])
    payload = {
        "intent": True,
        "max_tokens": 250,
        "model": "gpt-4",
        "n": 1,
        # Changed to False
        "stream": False,
        "temperature": 0.1,
        "top_p": 1,
        "messages": messages 
    }
    print("Post request...")
    resp = requests.post(url, json=payload, headers=headers, proxies=proxies)
    txt_resp = ""
    for i, msg in enumerate(resp.text.split("data: ")):
        try:
            msg = msg[:-2].replace("\n", "\\n")
            print(Fore.YELLOW, msg, Fore.RESET)
            json_data = json.loads(msg)
            content = json_data.get("choices")[0].get("delta").get("content")
            txt_resp += content
        except Exception as e:
            print(Fore.RED, i, e, msg, Fore.RESET)
    print(txt_resp)
    print("^^^^^^^ Above the response")

    #TODO
    def response_generator(resp):
        for i, msg in enumerate(resp.text.split("data: ")):
            try:
                msg = msg[:-2].replace("\n", "\\n")
                json_data = json.loads(msg)
                content = json_data.get("choices")[0].get("delta").get("content")
                yield litellm.ModelResponse(message=litellm.Message(content=content))
            except Exception as e:
                print(Fore.RED, i, e, msg, Fore.RESET)

    response_gen = response_generator(resp)
    return response_gen


def simple_send_with_retries(model_name, messages):
    try:
        _hash, response = send_with_retries(
            model_name=model_name,
            messages=messages,
            functions=None,
            stream=False,
        )
        return response.choices[0].message.content
    except (AttributeError, openai.BadRequestError):
        return
