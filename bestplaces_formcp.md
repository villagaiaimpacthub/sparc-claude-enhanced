# Best places to discover and install MCP servers for claude-code

The Model Context Protocol (MCP) ecosystem has rapidly evolved since its November 2024 launch, creating multiple avenues for discovering and installing servers. For claude-code users specifically, there are several excellent resources that combine easy discovery with streamlined installation processes.

## Official resources provide the foundation

The **official MCP servers repository** at `github.com/modelcontextprotocol/servers` serves as the primary source for stable, well-documented servers. Maintained by Anthropic with community contributions, it contains both reference implementations (Everything, Fetch, Filesystem, Git, Memory) and pre-built enterprise servers for major platforms like **Google Drive, Slack, GitHub, PostgreSQL, and Puppeteer**. The accompanying documentation at `modelcontextprotocol.io` provides comprehensive guides specifically tailored for Claude Desktop users, making this the most reliable starting point.

For claude-code users, the official Anthropic documentation at `docs.anthropic.com/en/docs/claude-code/mcp` offers specific installation guidance and best practices. The official registry service at `github.com/modelcontextprotocol/registry`, while still in early development, promises to become the standardized discovery mechanism for the entire ecosystem.

## Community collections offer breadth and innovation

The community has created several comprehensive collections that dramatically expand available options beyond official servers. The **punkpeye/awesome-mcp-servers** repository stands out with over 7,000 GitHub stars and 600+ curated servers, accessible through both GitHub and the searchable website at `glama.ai/mcp/servers`. This collection excels at categorization by use case, making it easy to find servers for specific needs like cloud services, databases, web APIs, or development tools.

Additional notable collections include **wong2/awesome-mcp-servers** (with its clean interface at `mcpservers.org`), **TensorBlock/awesome-mcp-servers** covering 7,260+ servers, and the **Docker MCP Catalog** at `hub.docker.com/mcp/` which provides security-focused, containerized distributions with over 1 million pulls.

## Claude-code installation is remarkably streamlined

Claude-code provides built-in installation capabilities that significantly simplify the process compared to manual configuration. The primary method uses the CLI wizard with commands like:

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/Projects
```

This approach handles all configuration automatically, storing settings in `~/.claude.json`. For team collaboration, claude-code supports project-scoped servers through `.mcp.json` files that can be version controlled. The platform also supports importing existing configurations from Claude Desktop and provides slash command integration where MCP server prompts become available as `/mcp__servername__promptname` commands.

Recent updates have added support for remote MCP servers with OAuth authentication, eliminating the need for local server management while providing automatic updates and vendor-hosted scalability.

## Emerging marketplaces simplify discovery

Several dedicated marketplaces have emerged to streamline MCP server discovery. **MCP Market** (`mcpmarket.com`) offers a curated collection with popularity metrics and direct installation links. **MCP.so** claims to be the largest collection with 11,790+ indexed servers and robust search functionality. **PulseMCP** (`pulsemcp.com/servers`) provides a clean interface with daily updates and excellent filtering capabilities.

For specific IDEs, **Cline MCP Marketplace** (`cline.bot/mcp-marketplace`) offers one-click installation, while **Cursor Directory** (`cursor.directory/mcp`) serves the Cursor IDE community. These platform-specific solutions often provide the smoothest installation experience through deep integration.

## Installation best practices for claude-code

Based on the research, the most effective approach for claude-code users follows this pattern:

**For getting started**, begin with essential servers using the CLI:
```bash
# Core functionality
claude mcp add sequential-thinking -s user -- npx -y @modelcontextprotocol/server-sequential-thinking
claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem ~/Projects
claude mcp add fetch -s user -- npx -y @kazuph/mcp-fetch
```

**For discovery**, browse the awesome-mcp-servers collections or marketplaces to find servers matching your needs. The community has standardized around clear categories: Cloud & DevOps, Databases, Web & APIs, Development Tools, Data & Analytics, AI & ML, Communication, and Security.

**For installation**, use claude-code's built-in CLI for simple setups, or edit `~/.claude.json` directly for complex configurations. Project-scoped installations using `.mcp.json` work best for team environments.

## Key considerations and recommendations

The MCP ecosystem shows remarkable growth with over 7,000 total servers available across all repositories and 200+ official integrations from major companies. The community's organization around standardized categories, quality indicators (using symbols like 🎖️ for official servers), and consistent documentation patterns makes navigation increasingly straightforward.

For claude-code users, the combination of official repositories for stability, community collections for variety, and built-in CLI tools for installation creates an efficient workflow. The emerging marketplace ecosystem promises even simpler discovery and installation processes, while remote MCP server support reduces local setup complexity.

The vibrant Discord community at `discord.gg/jHEGxQu2a5` with 8,500+ members provides real-time support for troubleshooting and discovering new servers. As the ecosystem matures, the official registry service will likely consolidate discovery further, but currently, the combination of official repos, awesome-lists, and emerging marketplaces provides comprehensive coverage for any MCP server needs.