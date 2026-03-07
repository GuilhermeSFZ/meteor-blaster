import json
import time
from socket import *

host = "0.0.0.0"
PORT = 12345 # Pelo que vi pela internet é bastante usada por ser facil de lembrar, mas necessita de cuidados por ser 
#uma porta comumente usada para práticas de netbus (aplicações maliciosas/malware)
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((host, PORT)) # O bind é necessário para o servidor, para que ele possa receber pacotes enviados para aquela porta
# permite que o servidor não trave esperando um pacote (0.1 segundos)
sock.settimeout(0.1)

print(f'Servidor seguro rodando em: {host}:{PORT}')

clientes = [] 
ultimo_contato = {} # Guarda o timestamp do último pacote de cada IP
TIMEOUT_LIMITE = 5.0 # após 5s, o cliente é considerado inativo e removido da lista de clientes

while True:
    try:
        try:
            dados_brutos, endereco = sock.recvfrom(4096)
            alive = time.time()
            ultimo_contato[endereco] = alive # Registra que o cliente está vivo

            # 1. VALIDAÇÃO DE DADOS
            try:
                data = json.loads(dados_brutos.decode())
                if not isinstance(data, dict) or "type" not in data:
                    continue
            except:
                continue

            # 2. GERENCIAMENTO DE CONEXÃO
            if endereco not in clientes:
                if len(clientes) < 2:
                    clientes.append(endereco)
                    print(f'Jogador {endereco} conectado. Total: {len(clientes)}')
                    
                    if len(clientes) == 2:
                        msg_ready = json.dumps({"type": "room_ready"}).encode()
                        for c in clientes:
                            sock.sendto(msg_ready, c)
                else:
                    # Servidor cheio, apenas ignora novas conexões
                    continue 

            # 3. Retransmissão de dados 
            # Somente retransmite se houver 2 jogadores, e apenas para o outro jogador (não ecoa para o remetente)
            if len(clientes) == 2:
                for cliente in clientes:
                    if cliente != endereco:
                        try:
                            sock.sendto(dados_brutos, cliente)
                        except:
                            pass

        except timeout:
            # Caso em que o recvfrom parou de esperar, então apenas segue para checar inatividade
            pass

        # 4. MONITORAMENTO DE INATIVIDADE (Heartbeat Check)
        alive = time.time()
        for cli in clientes[:]: # Itera sobre uma cópia da lista
            if alive - ultimo_contato.get(cli, 0) > TIMEOUT_LIMITE:
                print(f'Jogador {cli} removido por timeout (inatividade).')
                if cli in clientes: clientes.remove(cli)
                if cli in ultimo_contato: del ultimo_contato[cli]

    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        break

sock.close()