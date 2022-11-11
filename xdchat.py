import threading
import time
import rich.console

console = rich.console.Console()


class XDChat:

    def __init__(self, config):
        self.config = config
        self.users = {}
        self.messages = []
        self.not_read_message = {}
        self.clear = threading.Thread(target=lambda: self.message_clear())
        self.clear.start()

    def message_clear(self):
        console.log("[I] Clear thread started")
        while True:
            if self.messages.__len__() >= self.get_config(
                    "cache_clear")["start_count"]:
                self.messages.pop(0)
            time.sleep(self.get_config("cache_clear")["sleep"])

    def sent_message_log(self, message, addr):
        console.log(
            f"[I] [Chat] <{self.users[addr[1]]['name']}({self.users[addr[1]]['addr'][0]})> {message}"
        )

    def server_message_log(self, message):
        console.log(f"[I] [Chat] <Server(127.0.0.1)> {message}")

    def is_login(self, addr):
        return addr[1] in list(self.users.keys())

    def get_config(self, key):
        return self.config[key]

    def login(self, username, addr, password=""):
        if password == self.config["password"]:
            if username not in self.users.keys():    
                self.users[addr[1]] = {"name": username, "addr": addr}
                self.not_read_message[addr[1]] = self.messages.copy()
                self.send_server_message(
                    f"{self.users[addr[1]]['name']} join this server")
            else:
                raise NameError("User still online")
        else:
            raise ValueError("Wrong Password")

    def send_message(self, message, addr):
        self.sent_message_log(message, addr)
        msg = {
            "username": self.users[addr[1]]["name"],
            "text": message,
            "time": time.time()
        }
        self.messages += [msg]
        for user in self.not_read_message.keys():
            self.not_read_message[user] += [msg]

    def send_server_message(self, message):
        self.server_message_log(message)
        msg = {"username": "Server", "text": message, "time": time.time()}
        self.messages += [msg]
        for user in self.not_read_message.keys():
            self.not_read_message[user] += [msg]

    def get_not_read_message(self, addr):
        try:
            return [self.not_read_message[addr[1]].pop(0)]
        except IndexError:
            return []

    def get_list(self):
        users = []
        for user in self.users.values():
            users += [user["name"]]
        return users

    def logout(self, addr):
        self.send_server_message(
            f"{self.users[addr[1]]['name']} leave from this server")
        self.not_read_message.pop(addr[1])
        self.users.pop(addr[1])
