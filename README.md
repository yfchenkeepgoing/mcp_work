# Readme

- Install uv, run uv init to build the env

  - Install python in Dev Box

    Only use Microsoft Store to install Python. It will not work if you download and install python from the official website

  - Install uv on Dev Box (windows), run the following command in PowerShell

    ```powershell
    irm https://astral.sh/uv/install.ps1 | iex
    ```

    restart powershell to verify uv version

    ```powershell
    uv --version
    ```

  - delete `.venv`, run the following command to build the env

    ```powershell
    uv sync
    ```

- Activate the virtual env

  ```powershell
  PS C:\Users\xxx\mcp_work> .\.venv\Scripts\Activate.ps1
  ```

- No need to install fastmcp. Already installed when `uv sync`, you can check its version

  ```python
  fastmcp --version
  ```

- Run `server.py` to spin up the MCP server

  ```python
  fastmcp run server.py:mcp --transport sse --port 8000
  ```

- Double click `upload.html` to open it on edge

- Create a simple hello world file to drag and drop into the webpage

  e.g. simple hello world file `yifan-hello-world.txt`

  ```
  title: yifan-hello-world
  description: a hello world file created by yifan
  content: yifan says: Hello World!
  ```

- Check the log output on the server to confirm it arrived successfully into the server. If you see the following log output, it means the file has been successfully uploaded to the MCP server as resources

  ```
  INFO:server_module:Received upload request for file: yifan-hello-world.txt
  INFO:server_module:Read 109 bytes from yifan-hello-world.txt
  INFO:server_module:Successfully registered resource: yifan-hello-world.txt with URI doc://yifan-hello-world.txt
  INFO:     127.0.0.1:61484 - "POST /upload HTTP/1.1" 201 Created
  ```

- Run the following two commands to list and read resources

  ```python
  python .\list_resources.py
  python .\read_resource.py
  ```

  the two python commands were just handy utility scripts to confirm that everything worked smoothly

  The outcome is like:

  ```
  (mcp-work) PS C:\Repos\MCP\mcp_work> python .\list_resources.py
  [
    {
      "name": "yifan-hello-world.txt",
      "title": null,
      "uri": "doc://yifan-hello-world.txt",
      "description": "Text file yifan-hello-world.txt",
      "mimeType": "text/plain",
      "size": null,
      "annotations": null,
      "meta": null
    }
  ]
  ```

  ```
  (mcp-work) PS C:\Repos\MCP\mcp_work> python .\read_resource.py
  Available resources:
    - yifan-hello-world.txt (doc://yifan-hello-world.txt)
  
  --- Reading content of yifan-hello-world.txt ---
  Text content:
  title: yifan-hello-world
  description: a hello world file created by yifan
  content: yifan says: Hello World!
  ```

  