"""
Client registry
"""
from nicegui import app

class ClientRegistry:
    def __init__(self):
        self.clients = {}

    def add_client(self,client_id,client):
        self.clients[client_id] = client
    
    def remove_client(self,client_id):
        self.clients.pop(client_id, None)

client_registry = ClientRegistry()
