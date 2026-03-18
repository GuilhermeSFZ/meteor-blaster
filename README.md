# Meteor Blaster: A Network Multiplayer Game
**Destruidor de Meteoros** é um arcade de tiro espacial cooperativo onde dois jogadores precisam unir forças para defender a base. Desenvolvido em **Python** com a biblioteca **Pyxel**, o foco do projeto é a comunicação de baixa latência via **Sockets UDP**.

> 🎓 *Este projeto foi desenvolvido para a disciplina de Redes de Computadores.*

---

## 📋 Pré-requisitos

Antes de rodar o jogo, instale o Python e a biblioteca Pyxel em ambos os computadores:

```bash
# Instalação do Pyxel
pip install pyxel

# No Linux (Ubuntu/Debian), caso necessário para drivers de som/imagem:
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
´´
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
´´
