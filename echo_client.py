import socket
import json

class EchoClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False) 
        self.buffer_size = 4096 

    def receive_data(self):
        """Recebe dados e os converte de JSON para dicionário Python."""
        try:
            data, _ = self.sock.recvfrom(self.buffer_size)
            return json.loads(data.decode()) # Converte string JSON para dict
        except (BlockingIOError, socket.error):
            return None
        except Exception as e:
            # Se receber algo que não é JSON, ignora para não quebrar o jogo
            return None

    def send_data(self, data_dict):
        """Recebe um dicionário e envia como string JSON."""
        try:
            # Converte dict para string JSON antes de enviar
            msg = json.dumps(data_dict).encode()
            self.sock.sendto(msg, self.server_address)
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")
    
    def connect(self, player_id):
        self.send_data({"type": "login", "id": player_id})

    def close(self):
        self.sock.close()