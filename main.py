import rich.console
import init
import server
import sys

console = rich.console.Console()
version = "1.2.1"

if __name__ == "__main__":
    console.print(f"[green]XD[yellow]Chat [/]V{version}")
    config = init.init()
    sys.exit(server.start(config))
