import asyncio
from fastmcp import Client
from fastmcp.client.transports import SSETransport

SERVER = "http://localhost:8000/sse"

async def main():
    async with Client(SSETransport(SERVER)) as client:
        # First, list all resources to see what's available
        resources = await client.list_resources()
        print("Available resources:")
        for resource in resources:
            print(f"  - {resource.name} ({resource.uri})")

        if not resources:
            print("No resources found")
            return

        # Read and display each resource's content
        for res in resources:
            print(f"\n--- Reading content of {res.name} ---")
            content = await client.read_resource(res.uri)

            if content and len(content) > 0:
                resource_content = content[0]  # usually single item
                if hasattr(resource_content, "text"):
                    print(f"Text content:\n{resource_content.text}")
                elif hasattr(resource_content, "blob"):
                    print(f"Binary content: {len(resource_content.blob)} bytes")
                    try:
                        decoded = resource_content.blob.decode("utf-8")
                        print(f"Decoded text:\n{decoded}")
                    except:
                        print("Binary data (cannot decode as text)")
                else:
                    print(f"Unknown content type: {type(resource_content)}")

asyncio.run(main())