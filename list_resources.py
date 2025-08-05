import asyncio, json
from fastmcp import Client
from fastmcp.client.transports import SSETransport   # helper for SSE

SERVER = "http://localhost:8000/sse"                 # matches server log

async def main():
    # connect once and auto-close when done
    async with Client(SSETransport(SERVER)) as client:
        resources = await client.list_resources()    # returns list[Resource]

        # convert each Pydantic model to plain-json-safe dict
        data = [r.model_dump(mode="json") for r in resources]

        print(json.dumps(data, indent=2))

asyncio.run(main())