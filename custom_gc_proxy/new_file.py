import os
import litellm
import ipdb
import json

litellm.set_verbose=False# 👈 this is the 1-line change you need to make

def bye():
    print()

def hello_world():
    print("Hello, world!")

def main_gpt3():
    # set env variables
    #os.environ["OPENAI_API_KEY"] = "your-openai-key"

    ## SET MAX TOKENS - via completion() 
    response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{ "content": "Hello, how are you?","role": "user"}],
            max_tokens=10
        )

    print(response)
    ipdb.set_trace()


def main_ollama():
    # set env variables
    #os.environ["OPENAI_API_KEY"] = "your-openai-key"

    ## SET MAX TOKENS - via completion() 
    response = litellm.completion(
            model="ollama/llama3",
            messages=[{ "content": "Hello, how are you?","role": "user"}],
            max_tokens=10
        )

    print(response)


def main_copilot(MODEL="my_custom/gpt-3.5"):
    
    """
    NachoV Custom completation call.

    It must get a generator that returns ModelResponse
    """
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
    kwargs = {
            'custom_llm_provider': MODEL.split("/")[0], 
            'model': MODEL,
            'n': 1,
            'temperature': 0.1,
            'max_tokens': 25,
            #'intent': True,
            'top_p': 1,
            'base_url': 'https://api.githubcopilot.com/chat/completions',
            'api_base': 'https://api.githubcopilot.com/chat/completions',
            'headers': my_headers,
            # Added this stream: False
            'stream': False,
        }

    ## Just and nice example
    messages = [ 
            {
                "content": "You are an AI programming assistant.\nWhen asked for your name, you must respond with \"GitHub Copilot\".\nFollow the user's requirements carefully & to the letter.\nFollow Microsoft content policies.\nAvoid content that violates copyrights.\nIf you are asked to generate content that is harmful, hateful, racist, sexist, lewd, violent, or completely irrelevant to software engineering, only respond with \"Sorry, I can't assist with that.\"\nKeep your answers short and impersonal.\nYou can answer general programming questions and perform the following tasks: \n* Ask a question about the files in your current workspace\n* Explain how the code in your active editor works\n* Review the selected code in your active editor\n* Generate unit tests for the selected code\n* Propose a fix for the problems in the selected code\n* Scaffold code for a new workspace\n* Create a new Jupyter Notebook\n* Find relevant code to your query\n* Propose a fix for the a test failure\n* Ask questions about VS Code\n* Generate query parameters for workspace search\n* Ask about VS Code extension development\n* Ask how to do something in the terminal\n* Explain what just happened in the terminal\nYou use the GPT-4 version of OpenAI's GPT models.\nFirst think step-by-step - describe your plan for what to build in pseudocode, written out in great detail.\nThen output the code in a single code block.\nMinimize any other prose.\nUse Markdown formatting in your answers.\nMake sure to include the programming language name at the start of the Markdown code blocks.\nAvoid wrapping the whole response in triple backticks.\nThe user works in an IDE called Visual Studio Code which has a concept for editors with open files, integrated unit test support, an output pane that shows the output of running the code as well as an integrated terminal.\nThe user is working on a Windows machine. Please respond with system specific commands if applicable.\nThe active document is the source code the user is looking at right now.\nYou can only give one reply for each conversation turn.\n",
                "role": "system"
            },
            {
                "content": "Help me ",
                "role": "user"
            },
        ]

    #messages = kwargs.get("messages") + [{"role": "user", "content": "Help me with what I've asked for."}]
    print(messages[-1])
         
    # payload = {
    #     "intent": True,
    #     "max_tokens": 250,
    #     "model": MODEL,
    #     "n": 1,
    #     "stream": True,
    #     "temperature": 0.1,
    #     "top_p": 1,
    #     "messages": messages 
    # }
    print("litellm.completion()...")

    kwargs.update({"messages": messages})
    res = litellm.completion(**kwargs)
    #resp = requests.post(url, json=payload, headers=headers)
    # txt_resp = ""
    # for i, msg in enumerate(resp.text.split("data: ")):
    #     try:
    #         msg = msg[:-2].replace("\n", "\\n")
    #         print(Fore.YELLOW, msg, Fore.RESET)
    #         json_data = json.loads(msg)
    #         content = json_data.get("choices")[0].get("delta").get("content")
    #         txt_resp += content
    #     except Exception as e:
    #         print(Fore.RED, i, e, msg, Fore.RESET)
    # print(txt_resp)
    # print("^^^^^^^ Above the response")

    # #TODO
    # def response_generator(resp):
    #     for i, msg in enumerate(resp.text.split("data: ")):
    #         try:
    #             msg = msg[:-2].replace("\n", "\\n")
    #             json_data = json.loads(msg)
    #             content = json_data.get("choices")[0].get("delta").get("content")
    #             yield litellm.ModelResponse(message=litellm.Message(content=content))
    #         except Exception as e:
    #             print(Fore.RED, i, e, msg, Fore.RESET)

    # response_gen = response_generator(resp)
    # return response_gen
    print(res)
    print("^^^^^^^ Above the response")
    ipdb.set_trace()

if __name__ == "__main__":
    hello_world()
    #main_gpt3()
    #main_ollama()
    main_copilot()
