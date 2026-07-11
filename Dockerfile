# Container image for the agent-market-signals MCP server.
# Builds a self-contained image that runs the stdio MCP server, so indexers
# (e.g. Glama) and hosts can start it and introspect its tools.
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Install the package with the optional MCP server dependency.
RUN pip install --no-cache-dir ".[mcp]"

# The MCP server speaks over stdio.
ENTRYPOINT ["agent-market-signals-mcp"]
