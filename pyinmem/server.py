import logging
import re
import socket
import threading

from .core import PyInMemStore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PyInMemStoreServer:
    """
    A server class for handling TCP connections and executing store operations.
    """

    def __init__(self, host="127.0.0.1", port=5599):
        self.store = PyInMemStore()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.running = True

    def start(self):
        logger.info("Server started, waiting for connections...")
        try:
            while self.running:
                client, addr = self.server.accept()
                logger.info("Connected to %s", addr)
                threading.Thread(target=self.handle_client, args=(client,)).start()
        finally:
            self.server.close()

    def stop(self):
        self.running = False
        self.server.close()
        logger.info("Server stopped.")

    def handle_client(self, client):
        try:
            command_buffer = ""
            while True:
                data = client.recv(1024).decode()
                if not data:
                    break

                command_buffer += data
                if "\n" in command_buffer:
                    commands = command_buffer.split("\n")
                    for cmd in commands[:-1]:
                        response = self.process_command(cmd)
                        client.sendall(response.encode() + b"\n")
                    command_buffer = commands[-1]

        except Exception as e:
            logger.error("Error handling client: %s", e)
        finally:
            client.close()

    def process_command(self, command):  # noqa: PLR0911
        try:
            parts = re.split(r"\s+", command.strip())
            cmd, args = parts[0].upper(), parts[1:]
            logger.info("Processing command: %s, args: %s", cmd, args)
            if cmd == "SET":
                self.store.set(*args)
                return "OK"
            elif cmd == "GET":
                return self.store.get(args[0]) or "None"
            elif cmd == "DELETE":
                self.store.delete(args[0])
                return "OK"
            elif cmd == "EXPIRE":
                self.store.expire(args[0], int(args[1]))
                return "OK"
            elif cmd == "TTL":
                return str(self.store.ttl(args[0]))
            else:
                return "ERROR: Unknown Command or Incorrect Arguments"
        except Exception as e:
            return f"ERROR: {e}"


if __name__ == "__main__":
    server = PyInMemStoreServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
