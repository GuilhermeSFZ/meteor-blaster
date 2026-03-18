# Meteor Blaster: A Network Multiplayer Game
Um jogo de tiro espacial cooperativo desenvolvido em Python utilizando a biblioteca Pyxel. O projeto utiliza comunicação via Símbolos UDP para permitir que dois jogadores destruam meteoros em tempo real na mesma rede local. Esse projeto desenvolvido para a disciplina de Redes de Computadores.

## 📋 Pré-requisitos

Antes de rodar o jogo, você precisará instalar o Python e a biblioteca Pyxel em ambos os computadores.

```bash
# Instalação do Pyxel
pip install pyxel

# No Linux (Ubuntu/Debian), caso necessário:
sudo apt install libasound2-dev libx11-dev

```markdown
## 📂 Estrutura do Projeto

```text
/
├── main.py            # Arquivo principal do jogo (Client)
├── echo_server.py     # Servidor que sincroniza os dados
├── echo_client.py     # Lógica de comunicação de rede
└── assets/
    └── recursos.pyxres # Sprites, sons e trilha sonora

```markdown
## 🚀 Como Jogar

**No Computador 1 (Jogador 1):**
```bash
python3 main.py <IP_DO_SERVIDOR> p1
python3 main.py <IP_DO_SERVIDOR> p2

´markdown
### ⌨️ Controles
| Ação | Jogador 1 (P1) | Jogador 2 (P2) |
| Movimentação |        |                |

