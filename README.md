# MCP News Scraper

A Model Control Protocol (MCP) server that provides news scraping capabilities for Khaleej Times. This service allows you to fetch headlines and article content programmatically.

## Features

- Get the latest headline from Khaleej Times
- Get all main headlines from Khaleej Times
- Get full article content including title, paragraphs, author, and date

## Prerequisites

- Python 3.8 or higher
- uv (Python package installer)
- typer (for CLI functionality)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mcp-news
```

2. Install dependencies using uv:
```bash
uv run mcp install main.py
```

3. If you encounter any typer-related errors, install it separately:
```bash
pip install --upgrade typer
```

## Running the Server

1. Initialize the MCP server:
```bash
uv init mcp-server-demo
cd mcp-server-demo
```

2. Start the server:
```bash
python main.py
```

## Available Tools

The server provides the following tools:

1. `get_khaleej_times()`: Returns the latest headline from Khaleej Times
2. `get_khaleej_times_all()`: Returns all main headlines from Khaleej Times
3. `get_khaleej_times_article(url)`: Returns the full content of an article from its URL

## Usage with Claude Desktop

1. Make sure the MCP server is running
2. In Claude Desktop, you can interact with the news scraper using the available tools
3. Example queries:
   - "Get me the latest headline from Khaleej Times"
   - "Show me all headlines from Khaleej Times"
   - "Get the content of this article: <article_name>"

## Project Structure

```
mcp-news/
├── main.py              # Main server file with MCP tools
├── news_sources/        # Directory containing news source implementations
│   └── khaleej_times.py # Khaleej Times specific scraping logic
└── README.md           # This file
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

