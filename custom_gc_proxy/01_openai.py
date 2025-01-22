import os 
import litellm
from litellm import completion

litellm.set_verbose=True

# openai call
response = completion(
    model = "gpt-3.5-turbo-instruct", 
    messages=[{ "content": "Hello, how are you?","role": "user"}],
    max_tokens=25,
)