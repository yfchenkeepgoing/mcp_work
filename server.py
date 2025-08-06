import logging
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.resources import TextResource, BinaryResource
from starlette.requests import Request
from starlette.responses import JSONResponse
from uuid import uuid4

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastMCP server
mcp = FastMCP("LocalDocServer")

# Pre-load the Contoso compliance document so it is always available
COMPLIANCE_URI = "doc://compliance-1"
compliance_content = (
    "# Contoso Organization Azure Compliance Rules\n\n"
    "## Resource Naming Conventions\n"
    '1. All Azure resources MUST start with the prefix "contoso"'
)

try:
    mcp.add_resource(
        TextResource(
            uri=COMPLIANCE_URI,
            name="compliance 1.md",
            title="Contoso Organization Azure Compliance Rules",
            description="Resource Naming Conventions",
            text=compliance_content
        )
    )
    logger.info(f"Preloaded compliance resource with URI {COMPLIANCE_URI}")
except Exception as exc:
    logger.debug(f"Compliance resource already registered: {exc}")

# Define allowed file extensions to prevent executable uploads
# In the future we will support pdf, jpg, jpeg and png if OpenAI Files is integrated instead of just OpenAI Chat Messages
# ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_EXTENSIONS = {".txt", ".md"}

# Custom route to handle file uploads
@mcp.custom_route("/upload", methods=["POST"])
async def upload_file(request: Request):
    form = await request.form()

    # Validate mandatory fields
    if "file" not in form:
        logger.warning("Upload rejected: no file part in form")
        return JSONResponse({"error": "No file provided"}, status_code=400)
    if "description" not in form or not str(form["description"]).strip():
        logger.warning("Upload rejected: description is missing")
        return JSONResponse({"error": "Description is required"}, status_code=400)

    upload = form["file"]
    description_value = str(form["description"]).strip()
    filename = upload.filename
    
    logger.info(f"Received upload request for file: {filename}")
    
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected file {filename} - disallowed extension: {ext}")
        return JSONResponse({"error": "File type not allowed"}, status_code=400)
    
    data = await upload.read()
    file_size = len(data)
    logger.info(f"Read {file_size} bytes from {filename}")
    
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
    
    uri = f"doc:///{uuid4()}"
    title = Path(filename).stem

    if ext in [".txt", ".md"]:
        text_content = data.decode("utf-8")
        resource = TextResource(
            uri=uri,
            name=filename,
            title=title,
            description=description_value, # user input
            text=text_content
        )
    else:
        resource = BinaryResource(
            uri=uri,
            name=filename,
            title=title,
            description=description_value, # user input
            blob=data
        )

    mcp.add_resource(resource)
    logger.info(f"Successfully registered resource: {filename} with URI {resource.uri}")
    
    return JSONResponse({
        "status": "success",
        "uri": str(resource.uri),
        "size": file_size,
        "description": description_value,
        "disk_path": str(file_path)
    }, status_code=201)

if __name__ == "__main__":
    logger.info("Starting FastMCP server on http://localhost:8000")
    mcp.run(transport="sse", host="localhost", port=8000)