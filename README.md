Markdown
# ☄️ Meteor Blaster: A Network Multiplayer Game

**Destruidor de Meteoros** é um arcade de tiro espacial cooperativo onde dois jogadores precisam unir forças para defender a base. Desenvolvido em **Python** com a biblioteca **Pyxel**, o foco do projeto é a comunicação de baixa latência via **Sockets UDP**.

> 🎓 *Este projeto foi desenvolvido para a disciplina de Redes de Computadores na UFMT.*

---

## 📋 Pré-requisitos

Antes de rodar o jogo, instale o Python e a biblioteca Pyxel em ambos os computadores:

```bash
# Instalação do Pyxel
pip install pyxel

# No Linux (Ubuntu/Debian), caso necessário para drivers de som/imagem:
sudo apt install libasound2-dev libx11-dev
📂 Estrutura do ProjetoPlaintext/
├── main.py            # Arquivo principal do jogo (Client)
├── echo_server.py     # Servidor que sincroniza os dados
├── echo_client.py     # Lógica de comunicação de rede
└── assets/
    └── recursos.pyxres # Sprites, sons e trilha sonora (Essencial!)
🚀 Como Jogar1. Iniciar o ServidorEscolha uma máquina para ser o host (pode ser a mesma do P1) e execute:Bashpython3 echo_server.py
Anote o IP desta máquina (use hostname -I no Linux).2. Iniciar os ClientesSubstitua <IP_DO_SERVIDOR> pelo endereço IP da máquina que está rodando o servidor.No Computador 1 (Jogador 1 - Nave Amarela):Bashpython3 main.py <IP_DO_SERVIDOR> p1
No Computador 2 (Jogador 2 - Nave Roxa):Bashpython3 main.py <IP_DO_SERVIDOR> p2
⌨️ Controles de CombateAçãoJogador 1 (P1)Jogador 2 (P2)Mover para EsquerdaTecla ASeta EsquerdaMover para DireitaTecla DSeta DireitaAtirarTecla EspaçoTecla Enter ou Clique MouseNavegação MenusMouse / CliqueMouse / Clique🛠️ Detalhes TécnicosProtocolo: UDP para envio de pacotes de posição e eventos de disparo.Sincronização: O Jogador 1 (Host) gerencia o nascimento dos meteoros para garantir consistência entre as telas.Meteoro Especial: Meteoros vermelhos ativam uma explosão de área (raio de 150px) ao serem destruídos
