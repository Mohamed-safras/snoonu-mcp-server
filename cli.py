import argparse
import asyncio
import uvicorn
from src.server import app, mcp
from src.config.settings import settings

def cmd_server(args):
    if args.stdio:
        mcp.run(transport="stdio")
    else:
        uvicorn.run(app, host="0.0.0.0", port=settings.port)

def cmd_list_tools(_args):
    for tool in asyncio.run(mcp.list_tools()):
        print(tool.name)

def cmd_health(_args):
    from sqlalchemy import text
    from src.api.database.session import engine
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("OK")

def main():
    parser = argparse.ArgumentParser(prog="snoonu-mcp-server")
    sub = parser.add_subparsers(dest="command", required=True)

    p_server = sub.add_parser("server")
    p_server.add_argument("--stdio", action="store_true")
    p_server.set_defaults(func=cmd_server)

    sub.add_parser("list-tools").set_defaults(func=cmd_list_tools)
    sub.add_parser("health").set_defaults(func=cmd_health)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
