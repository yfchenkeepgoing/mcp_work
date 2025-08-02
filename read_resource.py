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
        
        if resources:
            # Read the first resource's content
            first_resource = resources[0]
            print(f"\n--- Reading content of {first_resource.name} ---")
            
            # Read the resource content
            content = await client.read_resource(first_resource.uri)
            
            # Content is a list of ResourceContents objects
            if content and len(content) > 0:
                resource_content = content[0]  # Get the first (usually only) content item
                
                if hasattr(resource_content, 'text'):
                    print(f"Text content:\n{resource_content.text}")
                elif hasattr(resource_content, 'blob'):
                    print(f"Binary content: {len(resource_content.blob)} bytes")
                    try:
                        decoded = resource_content.blob.decode('utf-8')
                        print(f"Decoded text:\n{decoded}")
                    except:
                        print("Binary data (cannot decode as text)")
                else:
                    print(f"Unknown content type: {type(resource_content)}")
            else:
                print("No content found")

asyncio.run(main())