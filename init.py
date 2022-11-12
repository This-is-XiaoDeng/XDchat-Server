import json
import rich.console

console = rich.console.Console()


def init():
    try:
        config = json.load(open("config.json"))
    except FileNotFoundError or json.JSONDecodeError:
        console.print("[bold red]XDChat Server Create Guide")
        config = {
            "host": {
                "IP": "",
                "port": int(console.input("[blue]Server Port?[/] "))
            },
            "max_connect": 1024,
            "welcome_message": "Welcome to this XDChat server!",
            "password": "",
            "cache_clear": {
                "start_count": 10,
                "sleep": 10
            },
            "bans": []
        }
        json.dump(config, open("config.json", "w"))
    # Bans
    if "bans" not in config.keys():
        config["bans"] = []
        json.dump(config, open("config.json", "w"))
    return config
