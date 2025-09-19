"""
Simple Time Server MCP - Just tells you what time it is now
To run your server, use "uv run dev"
To test interactively, use "uv run playground"
"""

from datetime import datetime
import zoneinfo

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from smithery.decorators import smithery


# Simple configuration
class TimeConfig(BaseModel):
    timezone: str = Field("UTC", description="Your timezone (e.g., Asia/Singapore, US/Eastern)")


@smithery.server(config_schema=TimeConfig)
def create_server():
    """Create the simple Time MCP server."""
    
    server = FastMCP("Clock")

    @server.tool()
    def current_time(ctx: Context) -> str:
        """What time is it now?"""
        session_config = ctx.session_config
        
        try:
            tz = zoneinfo.ZoneInfo(session_config.timezone)
            now = datetime.now(tz)
        except Exception:
            # Fallback to UTC if timezone is invalid
            tz = zoneinfo.ZoneInfo("UTC")
            now = datetime.now(tz)
        
        time_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
            
        day_name = now.strftime("%A")
        
        return f"It's {time_str} on {day_name} ({session_config.timezone})"

    @server.resource("timezones://continents")
    def available_continents() -> str:
        """List of available continents/regions with timezone counts."""
        try:
            from collections import defaultdict
            
            timezones = sorted(zoneinfo.available_timezones())
            
            # Group timezones by continent using defaultdict
            grouped = defaultdict(list)
            for tz in timezones:
                continent = tz.split('/')[0] if '/' in tz else 'Other'
                grouped[continent].append(tz)
            
            # Build result using list comprehension and join
            continent_lines = [
                f"• {continent} ({len(tzs)} timezones)\n"
                f"  → Access: timezones://continents/{continent.lower()}\n"
                for continent, tzs in sorted(grouped.items())
            ]
            
            header = "Available Continents/Regions:\n\n"
            footer = f"\nTotal: {len(timezones)} timezones across {len(grouped)} regions"
            
            return header + "\n".join(continent_lines) + footer
            
        except Exception:
            return "Error loading continents"

    @server.resource("timezones://continents/{continent}")
    def continent_timezones(continent: str) -> str:
        """List timezones for a specific continent."""
        try:
            continent = continent.capitalize()
            timezones = sorted(zoneinfo.available_timezones())
            
            # Filter timezones using list comprehension
            continent_tz = [
                tz for tz in timezones
                if ('/' in tz and tz.split('/')[0] == continent) or
                   (continent == 'Other' and '/' not in tz)
            ]
            
            if not continent_tz:
                return f"No timezones found for continent: {continent}"
            
            # Build result with f-string and join
            timezone_list = "\n".join(f"• {tz}" for tz in continent_tz)
            return f"Timezones in {continent}:\n\n{timezone_list}\n\nTotal: {len(continent_tz)} timezones"
            
        except Exception:
            return f"Error loading timezones for {continent}"

    return server