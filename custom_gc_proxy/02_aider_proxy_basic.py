import os 
import dotenv


environ_set = dotenv.load_dotenv(dotenv.find_dotenv('aider/.env'), verbose=True, override=True)
# I want to set the loaded variables to the environment variables
# so that the aider command can use them

if environ_set:
    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
    # # set http(s) proxy variables
    os.environ['http_proxy'] = os.getenv('http_proxy', 'http://127.0.0.1:8080')
    os.environ['https_proxy'] = os.getenv('https_proxy', 'http://127.0.0.1:8080')
else:
    print("Environment variables not set")
    raise Exception("Environment variables not set")


message = "Tell me a programming or AI joke in less than 25 words."

# cmd line aider call
import subprocess

command = [
    "aider",
    "--model", "gpt-4o-mini",
    "--message", message,
    "--cache-prompts", 
    "--no-stream",
    "--cache-keepalive-pings", "5"
]

result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)
print(result.stderr)