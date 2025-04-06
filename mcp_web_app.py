from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import urllib.parse
import os
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("beatport-mcp")

# Create an MCP server
mcp = FastMCP("Beatport MCP")


# Add a Beatport artist search tool
@mcp.tool()
async def search_beatport_artists(artist_name: str) -> dict:
    """
    Search for artists on Beatport by name
    
    Args:
        artist_name: The name of the artist to search for
        
    Returns:
        A dictionary containing the artist search results
    """
    logger.info(f"Searching for Beatport artist: {artist_name}")
    
    # Encode the artist name for the URL
    encoded_name = urllib.parse.quote(artist_name)
    url = f"https://api.beatport.com/v4/catalog/artists/?name={encoded_name}"
    
    # Make the API request
    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
            "User-Agent": "MCP-BeatportClient/1.0"
        }
        response = await client.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Successfully retrieved results for artist: {artist_name}")
            return response.json()
        else:
            logger.error(f"Failed to fetch data from Beatport API: {response.status_code}")
            return {
                "error": True,
                "status_code": response.status_code,
                "message": f"Failed to fetch data from Beatport API: {response.text}"
            }


async def server_info(request: Request):
    """Return information about the server"""
    return JSONResponse({
        "server_name": "Beatport MCP",
        "description": "MCP server with Beatport API integration",
        "mcp_endpoint": "/mcp/sse",
        "messages_endpoint": "/mcp/messages/",
        "tools": ["search_beatport_artists"],
        "status": "healthy"
    })


async def health_check(request: Request):
    """Simple health check endpoint for monitoring"""
    return PlainTextResponse("OK")


# Create the SSE server transport
sse = SseServerTransport("/mcp/messages/")


# Define the SSE endpoint handler
async def handle_sse(request: Request):
    """Handle SSE connections"""
    logger.info("New SSE connection established")
    try:
        async with sse.connect_sse(
            request.scope, 
            request.receive, 
            request._send  # type: ignore[reportPrivateUsage]
        ) as streams:
            await mcp._mcp_server.run(
                streams[0],
                streams[1],
                mcp._mcp_server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Error in SSE connection: {str(e)}")
        raise


# Configure middleware for production
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, you should specify exact origins
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
]

# Create a Starlette application and mount the MCP server components
app = Starlette(
    debug=False,  # Set to False for production
    middleware=middleware,
    routes=[
        Route("/", endpoint=server_info),
        Route("/info", endpoint=server_info),
        Route("/health", endpoint=health_check),
        # MCP endpoints
        Route("/mcp/sse", endpoint=handle_sse),
        Mount("/mcp/messages/", app=sse.handle_post_message),
    ]
)


if __name__ == "__main__":
    # Get port from environment variable for Railway.app compatibility
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting Beatport MCP server on port {port}")
    logger.info(f"MCP SSE endpoint available at /mcp/sse")
    logger.info(f"MCP messages endpoint available at /mcp/messages/")
    
    # Run with host 0.0.0.0 to accept all incoming connections
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")