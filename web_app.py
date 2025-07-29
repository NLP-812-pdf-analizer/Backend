import uvicorn
import asyncio
from controller.main import app

async def main() -> None:
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="0.0.0.0",
            port=6080,
        )
    )
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

