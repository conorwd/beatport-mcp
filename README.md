# Beatport MCP API

A Model Context Protocol (MCP) server that provides access to the Beatport API for searching artists. This service can be used with AI assistants or MCP-compatible clients.

## Features

- Provides a tool to search for artists on Beatport by name
- Exposes MCP-compliant endpoints for AI agent access
- Designed for cloud deployment (Railway.app)

## Endpoints

- `/` or `/info` - Server information
- `/health` - Health check endpoint
- `/mcp/sse` - MCP SSE connection endpoint
- `/mcp/messages/` - MCP messages endpoint

## Deployment to Railway.app

### Prerequisites

1. Create a [Railway.app](https://railway.app/) account
2. Install the [Railway CLI](https://docs.railway.app/develop/cli) (optional)

### Deployment Steps

#### Using the Railway.app Dashboard

1. Create a new project in the Railway dashboard
2. Connect your GitHub repository or use the "Deploy from GitHub" option
3. Point to your repository containing this code
4. Railway will automatically detect the Procfile and deploy the application
5. Environment variables will be automatically set, including the PORT

#### Using the Railway CLI

```bash
# Login to Railway
railway login

# Initialize a new project (if not done already)
railway init

# Deploy the application
railway up
```

### Environment Variables

- `PORT` - Automatically set by Railway.app

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python mcp_web_app.py
```

## Using with AI Assistants

This MCP server allows AI assistants to search for artists on Beatport. The assistant can:

1. Connect to the MCP server at the `/mcp/sse` endpoint
2. Use the `search_beatport_artists` tool to query the Beatport API
3. Get structured data about artists including names, IDs, and URLs

## API Example

Tool call format:

```json
{
  "jsonrpc": "2.0",
  "method": "tool/call",
  "params": {
    "name": "search_beatport_artists",
    "arguments": {
      "artist_name": "Hernan Cattaneo"
    }
  },
  "id": "message-id"
}
```

Response will include artist data in the same format as the Beatport API.