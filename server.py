import socket
import json
import threading
import xdchat
import rich.console

console = rich.console.Console()
_exit = False


def handle(sock, addr: list, chat_server: xdchat.XDChat):
    try:
        while not _exit:
            resp_data = {"code": 0, "msg": None, "data": {}}
            try:
                recv_data = json.loads(sock.recv(1024))
                if chat_server.is_login(addr):
                    if recv_data["mode"] == "get_message":
                        resp_data["data"][
                            "message"] = chat_server.get_not_read_message(addr)
                        resp_data["code"] = 200
                        resp_data["msg"] = "OK"
                    elif recv_data["mode"] == "send":
                        chat_server.send_message(recv_data["data"]["message"],
                                                 addr)
                        resp_data["code"] = 200
                        resp_data["msg"] = "OK"
                    elif recv_data["mode"] == "getlist":
                        resp_data["data"]["list"] = chat_server.get_list()
                        resp_data["code"] = 200
                        resp_data["msg"] = "OK"

                elif recv_data["mode"] == "login":
                    console.log("[I]", recv_data)
                    if "password" not in list(recv_data["data"].keys()):
                        recv_data["data"]["password"] = ""
                    try:
                        chat_server.login(
                            username=recv_data["data"]["username"],
                            addr=addr,
                            password=recv_data["data"]["password"])
                    except KeyError as e:
                        resp_data["code"] = 401
                        resp_data["msg"] = str(e)
                    except ValueError as e:
                        resp_data["code"] = 402
                        resp_data["msg"] = str(e)
                    else:
                        resp_data["code"] = 200
                        resp_data["msg"] = "OK"
                        resp_data["data"]["message"] = chat_server.get_config(
                            "welcome_message")
            except Exception as e:
                console.print_exception()
                resp_data["code"] = 400
                resp_data["msg"] = str(e)
            sock.send(json.dumps(resp_data).encode("utf-8"))
    except BrokenPipeError:
        console.print_exception()
        chat_server.logout(addr)
        sock.close()


def run_command(chat_server: xdchat.XDChat, addr):
    global _exit
    while True:
        command = console.input("")
        if command[:3] == "say":
            chat_server.send_server_message(command[4:])
        elif command == "exit":
            chat_server.send_server_message("Server closed!")
            _exit = True
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(addr)
            break
        elif command == "list":
            online_list = chat_server.get_list()
            max_conn = chat_server.get_config("max_connect")
            console.log(
                f"[I] There are {len(online_list)}/{max_conn} user(s) online:",
                online_list
            )
        elif command == "help":
            console.log("""[I] Help:
help        Show help
say <msg>   Say <msg> in server
exit        Close server
list        Get a list of online users""")
        else:
            console.log("[yellow][W] Unkown command!")


def start(config):
    server_addr = (config["host"]["IP"], config["host"]["port"])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_addr)
    sock.listen(config["max_connect"])
    chat_server = xdchat.XDChat(config)
    console.log(f"[I] Server started on {server_addr}")
    command_thread = threading.Thread(
        target=lambda: run_command(chat_server, server_addr))
    command_thread.start()
    while not _exit:
        new_sock, addr = sock.accept()
        console.log(f"[I] {addr} connect to this server")
        threading.Thread(target=handle,
                         args=(new_sock, addr, chat_server)).start()
    console.log("[I] Server closed!")
    return 0
