# HTTP client used to make requests from the MCP server to the deployed API
import httpx
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Base URL of the deployed FastAPI backend on Railway
# All MCP tool requests will call this API rather than a local database
API_BASE_URL = "https://webservicescoursework-production.up.railway.app"

# Initialise the MCP server instance
# The name identifies this MCP service
mcp = FastMCP("travel-without-barriers")

# -----------------------------------------
# Helper function for error handling
# -----------------------------------------

def handle_error_response(response: httpx.Response) -> str:
    try:
        data = response.json()
        return data.get("detail") or data.get("message") or response.text
    except Exception:
        return response.text or f"Request failed with status {response.status_code}"

# -----------------------------------------
# MCP Tool: Get Destination Recommendations
# -----------------------------------------

@mcp.tool()
def get_recommendations(
    continent: Optional[str] = None,
    country: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_cost: Optional[float] = None,
    sort_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = {}

    if continent:
        params["continent"] = continent
    if country:
        params["country"] = country
    if min_rating is not None:
        params["min_rating"] = min_rating
    if max_cost is not None:
        params["max_cost"] = max_cost
    if sort_by:
        params["sort_by"] = sort_by

    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{API_BASE_URL}/recommendations", params=params)

    if response.status_code != 200:
        return [{"error": handle_error_response(response)}]

    return response.json()

# -----------------------------------------
# MCP Tool: Register User
# -----------------------------------------

@mcp.tool()
def register_user(email: str, password: str) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    clean_password = password.strip()

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": clean_email,
                "password": clean_password,
            },
        )

    if response.status_code != 200:
        return {"error": handle_error_response(response)}

    return response.json()

# -----------------------------------------
# MCP Tool: Login User
# -----------------------------------------

@mcp.tool()
def login_user(email: str, password: str) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    clean_password = password.strip()

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": clean_email,
                "password": clean_password,
            },
        )

    if response.status_code != 200:
        return {"error": handle_error_response(response)}

    return response.json()

# -----------------------------------------
# MCP Tool: List Wishlists
# -----------------------------------------

@mcp.tool()
def list_wishlists(email: str, password: str) -> List[Dict[str, Any]]:
    clean_email = email.strip().lower()
    clean_password = password.strip()

    with httpx.Client(timeout=30.0) as client:
        login_response = client.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": clean_email,
                "password": clean_password,
            },
        )

        if login_response.status_code != 200:
            return [{"error": handle_error_response(login_response)}]

        token = login_response.json()["access_token"]

        response = client.get(
            f"{API_BASE_URL}/wishlists",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        return [{"error": handle_error_response(response)}]

    return response.json()

# -----------------------------------------
# MCP Tool: Create Wishlist
# -----------------------------------------

@mcp.tool()
def create_wishlist(
    email: str,
    password: str,
    name: str,
    description: str = "",
) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    clean_password = password.strip()
    clean_name = name.strip()
    clean_description = description.strip()

    if not clean_name:
        return {"error": "Wishlist name cannot be blank"}

    with httpx.Client(timeout=30.0) as client:
        login_response = client.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": clean_email,
                "password": clean_password,
            },
        )

        if login_response.status_code != 200:
            return {"error": handle_error_response(login_response)}

        token = login_response.json()["access_token"]

        response = client.post(
            f"{API_BASE_URL}/wishlists",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": clean_name,
                "description": clean_description,
            },
        )

    if response.status_code != 200:
        return {"error": handle_error_response(response)}

    return response.json()

# -----------------------------------------
# MCP Tool: Delete Wishlist
# -----------------------------------------

@mcp.tool()
def delete_wishlist(
    email: str,
    password: str,
    wishlist_id: int,
) -> Dict[str, Any]:
    clean_email = email.strip().lower()
    clean_password = password.strip()

    with httpx.Client(timeout=30.0) as client:
        login_response = client.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": clean_email,
                "password": clean_password,
            },
        )

        if login_response.status_code != 200:
            return {"error": handle_error_response(login_response)}

        token = login_response.json()["access_token"]

        response = client.delete(
            f"{API_BASE_URL}/wishlists/{wishlist_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        return {"error": handle_error_response(response)}

    return response.json()

# -----------------------------------------
# MCP Prompt
# -----------------------------------------

@mcp.prompt()
def plan_low_stress_trip() -> str:
    return (
        "Help the user find low-stress travel destinations by prioritising "
        "affordability, lower crowd levels, and strong ratings. "
        "Use the available recommendation and wishlist tools before answering."
    )

# -----------------------------------------
# Run MCP Server
# -----------------------------------------

if __name__ == "__main__":
    mcp.run()