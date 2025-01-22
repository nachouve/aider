# Run mitmproxy in a container with the web interface exposed on port 8081
# Set proxy env variables in powershell
$env:HTTP_PROXY="http://127.0.0.1:8080"
set HTTP_PROXY=http://127.0.0.1:8080
set HTTPS_PROXY=https://127.0.0.1:8080

# Check the proxy variables in powershell
$env:HTTP_PROXY
echo %HTTP_PROXY%

 Set-ExecutionPolicy RemoteSigned -Scope Process

# Run the container
docker run --rm -it -p 8080:8080 -p 127.0.0.1:8081:8081 mitmproxy/mitmproxy mitmweb --web-host 0.0.0.0