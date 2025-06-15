from flask import Flask, jsonify, request
from mcp.server.fastmcp import FastMCP
import logging
import requests
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MCP server URL with trailing slash
MCP_SERVER_URL = "http://localhost:8000/mcp/"

def call_mcp_tool(tool_name: str, **kwargs):
    """Helper function to call MCP tools using JSON-RPC format"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": tool_name,
            "params": kwargs
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(
            MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=5,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Parse JSON response
        result = response.json()
        if "error" in result:
            raise Exception(result["error"])
        return result.get("result")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
        raise

@app.route('/')
def home():
    """Home endpoint that shows available endpoints"""
    return jsonify({
        "service": "News Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/": "This help message",
            "/ping": "Health check endpoint to verify service status",
            "/khaleej-times": "Get latest headline from Khaleej Times",
            "/khaleej-times/all": "Get all main headlines from Khaleej Times",
            "/khaleej-times/article": "Get full article content (POST with url parameter)"
        }
    })

@app.route('/ping')
def ping():
    """Health check endpoint that verifies both Flask app and MCP server are running"""
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "components": {
            "flask_app": "healthy",
            "mcp_server": "unhealthy"
        },
        "response_time_ms": 0
    }
    
    try:
        # Check MCP server health using JSON-RPC
        result = call_mcp_tool("ping")
        if result == "pong":
            health_status["components"]["mcp_server"] = "healthy"
    except requests.exceptions.RequestException as e:
        logger.error(f"MCP server health check failed: {str(e)}")
        health_status["status"] = "degraded"
    
    # Calculate response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Set overall status
    if health_status["components"]["mcp_server"] == "unhealthy":
        health_status["status"] = "degraded"
    
    return jsonify(health_status)

@app.route('/khaleej-times')
def khaleej_times():
    """Get latest headline from Khaleej Times"""
    try:
        result = call_mcp_tool("get_khaleej_times")
        return jsonify({"headline": result})
    except Exception as e:
        logger.error(f"Error fetching Khaleej Times headline: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/khaleej-times/all')
def khaleej_times_all():
    """Get all main headlines from Khaleej Times"""
    try:
        result = call_mcp_tool("get_khaleej_times_all")
        return jsonify({"headlines": result})
    except Exception as e:
        logger.error(f"Error fetching all Khaleej Times headlines: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/khaleej-times/article', methods=['POST'])
def khaleej_times_article():
    """Get the full content of a Khaleej Times article"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL parameter is required"}), 400
            
        result = call_mcp_tool("get_khaleej_times_article", url=data['url'])
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching Khaleej Times article: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 