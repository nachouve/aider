import litellm
import os

print("***** Let's start the gc_proxy test****")

API_BASE = "http://127.0.0.1:5000"

print(f"gc_proxy must be launched and listening over API_BASE: {API_BASE}")

litellm.set_verbose=True

response = litellm.completion(
    model="openai/mistral",               # add `openai/` prefix to model so litellm knows to route to OpenAI
    api_key="sk-1234",                  # api key to your openai compatible endpointº
    api_base=API_BASE,     # set API Base of your Custom OpenAI Endpoint
    messages=[
                {
                    "role": "user",
                    "content": "Hey, how's it going?",
                }
    ],
    temperature=0.1,
    max_tokens= 25,
            #'intent': True,
    top_p = 1,
    #         'base_url': 'https://api.githubcopilot.com/chat/completions',
    #         'api_base': 'https://api.githubcopilot.com/chat/completions',
    #         'headers': my_headers,
    #         # Added this stream: False
    #         'stream': False,
    verbose=True,
)

print("***"*50)
print("Response:")
print("***"*50)
print(response)
resp_json = response.json()
print("***"*50)

for i, choices in enumerate(resp_json["choices"]):
    print(i, f'{choices["message"]["role"]}:  {choices["message"]["content"]}')