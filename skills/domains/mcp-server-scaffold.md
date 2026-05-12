---
name: mcp-server-scaffold
description: >
  Scaffold new MCP (Model Context Protocol) servers with TypeScript/Node.js
  templates, stdio and HTTP transport configs, tool/resource templates, and
  package.json setup. Use when user wants to create a new MCP server, build
  an MCP tool server, set up MCP stdio transport, or scaffold MCP server boilerplate.
  Triggers on: "create MCP server", "scaffold MCP server", "new MCP tool server",
  "build MCP server", "MCP server template", "stdio MCP server", "HTTP MCP server".
metadata:
  tags: [mcp, server, scaffold, typescript, nodejs, template, stdio, http, tools, resources]
  tier: task-specific
  domain: tooling
---

# MCP Server Scaffold

Scaffold production-ready MCP servers with proper TypeScript/Node.js boilerplate,
transport configuration, and tool/resource handler patterns.

## When to Use

- User wants to create a new MCP server from scratch
- Setting up stdio transport for Claude Desktop integration
- Building HTTP/SSE transport for remote MCP servers
- Creating tool handlers with proper input schema validation
- Implementing resource providers with URI templates
- Adding notification handlers for progress/cancellation
- Need MCP server boilerplate with proper package.json setup

## What This Skill Does

1. **Project Setup** — Create package.json with MCP SDK dependencies
2. **Transport Selection** — Configure stdio (desktop) or HTTP/SSE (remote)
3. **Server Scaffold** — Generate main server.ts with proper initialization
4. **Tool Templates** — Add sample tool handlers with Zod schemas
5. **Resource Templates** — Add sample resource providers with URI patterns
6. **Build Config** — Set up TypeScript, tsconfig, and build scripts
7. **Integration Guide** — Document Claude Desktop or client integration

## Usage

```
/mcp-server-scaffold                    # Interactive setup
/mcp-server-scaffold --name my-server   # Set server name
/mcp-server-scaffold --transport stdio  # Force stdio transport
/mcp-server-scaffold --transport http   # Force HTTP transport
```

## Workflow

### Step 1: Gather Requirements

Determine:
- **Server name**: Project and package name (kebab-case)
- **Transport type**: `stdio` (Claude Desktop) or `http` (remote clients)
- **Tools**: List of tool names to scaffold (optional)
- **Resources**: List of resource URI patterns (optional)

### Step 2: Project Initialization

Create project structure:

```bash
mkdir <server-name>
cd <server-name>
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
npx tsc --init
```

### Step 3: Generate Server Files

Use bundled templates based on transport:

**For stdio (Claude Desktop):**
- Load template from `templates/typescript/template-server-stdio.ts` or `templates/python/template-server-stdio.py`
- Configure server for stdio transport
- Add `build` and `start` scripts to package.json

**For HTTP/SSE:**
- Load template from `templates/typescript/template-server-http.ts` or `templates/python/template-server-http.py`
- Configure Express server with SSE endpoints
- Add CORS and session management

Or use the helper script:
```bash
$SKILL_DIR/scripts/scaffold-mcp-server.sh --name my-server --transport stdio --language typescript
```

### Step 4: Add Tool Handlers

For each requested tool:
- Create handler in `src/tools/<tool-name>.ts` (or `.py`)
- Use template from `templates/typescript/template-tool.ts` or `templates/python/template-tool.py`
- Define Zod input schema (TypeScript) or Pydantic model (Python)
- Register in main server

### Step 5: Add Resource Providers

For each requested resource:
- Create provider in `src/resources/<resource-name>.ts` (or `.py`)
- Use template from `templates/typescript/template-resource.ts` (TypeScript only)
- Define URI template pattern
- Register in main server

### Step 6: Build & Verify

```bash
npm run build    # Compile TypeScript
npm start        # Test server starts
```

### Step 7: Integration Documentation

Generate README with:
- Installation steps
- Configuration for Claude Desktop (stdio) or client (http)
- Available tools and resources list
- Example usage

## File Index

| File | Purpose |
|------|---------|
| `templates/typescript/template-server-stdio.ts` | TypeScript MCP server with stdio transport for Claude Desktop |
| `templates/typescript/template-server-http.ts` | Express-based MCP server with HTTP/SSE transport |
| `templates/typescript/template-tool.ts` | Tool handler template with Zod schema validation |
| `templates/typescript/template-resource.ts` | Resource provider template with URI template |
| `templates/typescript/template-package.json` | package.json template with MCP SDK deps |
| `templates/python/template-server-stdio.py` | Python MCP server with stdio transport |
| `templates/python/template-server-http.py` | Python HTTP/SSE MCP server |
| `templates/python/template-tool.py` | Python tool handler template |
| `scripts/scaffold-mcp-server.sh` | CLI script for scaffolding new MCP servers |
| `references/mcp-protocol-guide.md` | MCP protocol overview and best practices |
| `references/stdio-integration.md` | Claude Desktop stdio integration steps |
| `references/http-integration.md` | HTTP/SSE transport setup and deployment |
| `assets/*` | Legacy template storage ( mirrored in templates/ ) |

## Examples

### Example 1: Weather MCP Server (stdio)

**Input**: "Create an MCP server called 'weather-mcp' with stdio transport and a 'get-forecast' tool"

**Output**:
- `weather-mcp/package.json` with MCP SDK
- `weather-mcp/src/server.ts` with stdio transport
- `weather-mcp/src/tools/get-forecast.ts` with location input schema
- `weather-mcp/README.md` with Claude Desktop config

### Example 2: Database Query Server (HTTP)

**Input**: "Scaffold an HTTP MCP server 'db-query-mcp' with a 'query' resource for SQL execution"

**Output**:
- `db-query-mcp/package.json` with Express + MCP SDK
- `db-query-mcp/src/server.ts` with HTTP transport
- `db-query-mcp/src/resources/query.ts` with parameterized SQL resource
- HTTP endpoint configuration for remote clients

## Related Skills

- `native-mcp` — Use existing MCP servers once configured
- `hermes-agent` — Configure Hermes Agent MCP client
- `skill-creator` — Pattern for creating new skills (similar structure)
