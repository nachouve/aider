
# OBJECTIVE

I want to get a aider-chat that works with GC, so with my personal account with fix monthly costs work with all magic of aider-chat.

Notes:
- ``ipython-copilot-completer`` project has functions to login and operates with GC.
- ``lite-llm`` is the way that aider use to communicate with LLMs and has way to customize that.

# STEPS

1- Create a fake  custom OPENAI compatible service to listen locally: myGC
2- Configure litellm to use it 
3- Program myGC functions to login, request and response properly 



# Interesting docs

https://docs.litellm.ai/docs/completion/input

Sobre Custom Endpoints:
https://github.com/BerriAI/litellm/discussions/1485

https://docs.litellm.ai/docs/providers/openai_compatible



# CAPTURE traffic

REM HTTP Proxy
set HTTP_PROXY=127.0.0.1:8080
set HTTPS_PROXY=127.0.0.1:8080

> docker run --rm -it -v C:/Users/nacho/.mitmproxy:/home/mitmproxy/.mitmproxy -p 8080:8080 -p 127.0.0.1:8081:8081 mitmproxy/mitmproxy mitmweb --web-host 0.0.0.0    ##  The -v for volume mount is optional. It allows to persist and reuse the generated CA certificates between runs, and for you to access them. Without it, a new root CA would be generated on each container restart.

Then we have the proxy running at port 8080, and a mitmproxy web interface at localhost:8081


We need to install certificates
https://docs.mitmproxy.org/stable/concepts-certificates/

Steps in windows
1. Install the user\.mitmproxy\mitmproxy-ca-cert.pem in windows by double click and next, next, next
2. python -c "import certifi; print(certifi.where())"
3. Open that location and append to the end of that file the ".mitmproxy\mitmproxy-ca-cert.pem"
4. Retry!!! Aider and curl must work perfectly!!


To run aider on a proxy:
 
python aider\main.py


# Capture traffic from VS Code

To configure Visual Studio Code to use a proxy, follow these steps:

### Step 1: Open Settings
1. Open Visual Studio Code.
2. Go to `File` > `Preferences` > `Settings` or press `Ctrl + ,`.

### Step 2: Search for Proxy Settings
1. In the search bar at the top of the Settings pane, type `proxy`.

### Step 3: Configure Proxy Settings
1. Look for the `Http: Proxy` setting.
2. Click on `Edit in settings.json` to open the `settings.json` file.

### Step 4: Add Proxy Configuration
1. Add the following lines to the `settings.json` file:

```json
{
    "http.proxy": "http://127.0.0.1:8080",
    "https.proxy": "http://127.0.0.1:8080",
    "http.proxyStrictSSL": false
}
```

### Step 5: Save and Restart
1. Save the `settings.json` file.
2. Restart Visual Studio Code to apply the changes.

### Example `settings.json` File
Here is an example of what your `settings.json` file might look like after adding the proxy settings:

```json
{
    "http.proxy": "http://127.0.0.1:8080",
    "https.proxy": "http://127.0.0.1:8080",
    "http.proxyStrictSSL": false,
    // other settings...
}
```

This configuration will route all HTTP and HTTPS traffic through the specified proxy server. The `http.proxyStrictSSL` setting is set to `false` to allow connections to servers with self-signed certificates.



## AIDER with my custom gc_proxy

aider --openai-api-base=http://127.0.0.1:4141 --show-prompts --chat-language=en



### 
Today using that code return absurd messages... Hummm... I think there is something that not match!!





### Run ollama in a docker

docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama 