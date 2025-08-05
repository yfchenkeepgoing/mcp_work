import logging
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.resources import TextResource, BinaryResource
from starlette.requests import Request
from starlette.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastMCP server
mcp = FastMCP("LocalDocServer")

# Define allowed file extensions to prevent executable uploads
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png"}

# Custom route to handle file uploads
@mcp.custom_route("/upload", methods=["POST"])
async def upload_file(request: Request):
    form = await request.form()
    if "file" not in form:
        return JSONResponse({"error": "No file provided"}, status_code=400)
    upload = form["file"]
    filename = upload.filename
    
    logger.info(f"Received upload request for file: {filename}")
    
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected file {filename} - disallowed extension: {ext}")
        return JSONResponse({"error": "File type not allowed"}, status_code=400)
    
    data = await upload.read()
    logger.info(f"Read {len(data)} bytes from {filename}")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    logger.info(f"Uploads directory: {uploads_dir.absolute()}")
    
    # Save file to disk
    file_path = uploads_dir / filename
    logger.info(f"Attempting to save to: {file_path.absolute()}")
    file_path.write_bytes(data)
    logger.info(f"Successfully saved file to disk: {file_path}")
    
    # Verify file was created
    if file_path.exists():
        logger.info(f"File verified on disk: {file_path} ({file_path.stat().st_size} bytes)")
    else:
        logger.error(f"File was NOT created on disk: {file_path}")
    
    if ext in [".txt", ".md"]:
        text_content = data.decode("utf-8")
        resource = TextResource(
            uri=f"doc://{filename}",
            name=filename, 
            description=f"Text file {filename} (saved to {file_path})",
            text=text_content
        )
    else:
        resource = BinaryResource(
            uri=f"doc://{filename}",
            name=filename, 
            description=f"Binary file {filename} (saved to {file_path})",
            blob=data
        )
        
    mcp.add_resource(resource)
    logger.info(f"Successfully registered resource: {filename} with URI {resource.uri}")
    
    return JSONResponse({
        "status": "success", 
        "uri": str(resource.uri), 
        "size": len(data),
        "disk_path": str(file_path)
    }, status_code=201)

# Add a route to list all resources
# @mcp.custom_route("/resources", methods=["GET"])
# async def list_resources(request: Request):
#     """List all registered resources"""
#     resources = []
#     # Access the resources from the MCP server
#     for uri, resource in mcp._resources.items():
#         resources.append({
#             "uri": uri,
#             "name": resource.name,
#             "description": resource.description,
#             "type": "text" if hasattr(resource, 'text') else "binary"
#         })
    
#     logger.info(f"Listing {len(resources)} registered resources")
#     return JSONResponse({"resources": resources, "count": len(resources)})

if __name__ == "__main__":
    logger.info("Starting FastMCP server on http://localhost:8000")
    mcp.run(transport="sse", host="localhost", port=8000)