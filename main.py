# Universidade Federal do Mato Grosso
# Disciplina: Redes de Computadores
# Discente: Guilherme da Silva Ferraz
# RGA: 202211722013
# Trabalho 1 - Jogo Multiplayer
import sys
import pyxel
import random 
from socket import *
from echo_client import EchoClient
WIDTH = 420 # Largura da tela
HEIGHT = 460 # Altura da tela

SPECIAL_EVERY = 10 # A cada 10 meteoros normais, um especial aparece
SPECIAL_SIZE = 64
SPECIAL_RADIUS = 150

# Classe para partículas de explosão dos meteoros
class Particula:
    def __init__(self, x, y):
        # Posição inicial (x, y) da partícula
        self.x = x 
        self.y = y
        # Velocidade aleatória (vx, vy)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.tdv = 1.0  # Tempo de vida (1.0 a 0.0)
        self.cor = random.choice([7, 10, 13, 8]) # Cores: Branco, Amarelo, Laranja, Vermelho


    def atualizar(self): # Atualiza a posição das partículas e o tempo de vida delas
        self.x += self.vx
        self.y += self.vy
        self.tdv -= 0.05  # Diminui o tempo de vida da partícula em 5% a cada frame
    def desenhar(self):
        if self.tdv > 0: # Desenha apenas se ainda estiver "viva"
            raio = self.tdv * 2 # Calcula o raio com base no tempo de vida e define até onde as partículas podem ir
            pyxel.circ(self.x, self.y, raio, self.cor) # Desenha a partícula como um círculo

class Game:
    def __init__(self): #Inicialização do jogo
        # Pega o IP e o ID do jogador do terminal: python3 main.py <IP> <p1 ou p2>
        self.server_ip = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0" 
        self.player_id = sys.argv[2] if len(sys.argv) > 2 else "p1" # "p1" para o jogador 1 e "p2" para o jogador 2
        
        self.network = EchoClient(self.server_ip, 12345) 
        self.network.connect(self.player_id) # Envia o id do jogador para o servidor
        
        pyxel.init(WIDTH, HEIGHT, title="Destruidor de Meteoros") 
        pyxel.mouse(True)
        # Carregando meteoros, background e naves
        try:
            pyxel.load("assets/recursos.pyxres")
        except:
            pass

        # Estado inicial do jogo
        self.state = "menu"
        self.player1_x = WIDTH // 2 - 40 # Posicão inicial do jogador 1 (nave amarela e marrom)
        self.player2_x = WIDTH // 2 + 10 # Posição inicial do jogador 2 (nave rosa e roxa)
        self.player_y = HEIGHT - 50 
        self.score_p1 = 0
        self.score_p2 = 0
        self.bullets_p1 = []
        self.bullets_p2 = []
        self.meteors = []
        self.meteor_count = 0
        self.difficulty = 1
        self.explosions = []
        self.jogadores_prontos = False
        self.remote_level_chosen = False
        self.remote_difficulty = None
        self.waiting_start_time = None # Variável para controlar o tempo de espera na tela de "aguardando_nivel"
        self.connection_timeout = 30 # 30 segundos de limite para o outro jogador entrar
        #Musica de fundo (banco 0, musica 0) - Loop infinito
        pyxel.playm(0, 0, loop=True) # Inicio minha musica de fundo
        pyxel.run(self.update, self.draw)

    # Primeira tela, menu, regras e jogo
    def update(self):
        # 1. Recebe dados da rede e processa mensagens 
        data = self.network.receive_data()
        
        if data and isinstance(data, dict): # Se é um dado válido e se é do tipo dicionário, processa ele
            tipo = data.get("type")
            
            if tipo == "room_ready":
                self.jogadores_prontos = True
                self.waiting_start_time = None # Reseta o tempo de espera, já que ambos os jogadores estão prontos
            
            # Recebe a escolha de nível do outro jogador, para garantir que ambos joguem no mesmo nível 
            elif tipo == "choose_level":
                self.remote_difficulty = data.get("val")
            
            elif tipo == "status": 
                if data["id"] == "p1" and self.player_id == "p2": 
                    #Se for o status do jogador 1 e eu for o jogador 2, atualizo a posição do jogador 1 e a pontuação dele
                    self.player1_x = data["x"]
                    self.score_p1 = data.get("score", self.score_p1)
                elif data["id"] == "p2" and self.player_id == "p1":
                    #Se for o status do jogador 2 e eu for o jogador 1, atualizo a posição do jogador 2 e a pontuação dele
                    self.player2_x = data["x"]
                    self.score_p2 = data.get("score", self.score_p2)
            
            elif tipo == "shoot": # Se é o estado de um tiro, toca o som de tiro e adiciona a bala na lista do jogador correspondente
                pyxel.play(0, 1) 
                p_shooter = data.get("id")
                # Se recebi a confirmação de que o P1 atirou e eu sou o P2, registro a bala do P1 localmente e vice-versa
                if p_shooter == "p1" and self.player_id == "p2": 
                    self.bullets_p1.append([self.player1_x + 14, self.player_y, "p1"]) 
                elif p_shooter == "p2" and self.player_id == "p1":
                    self.bullets_p2.append([self.player2_x + 14, self.player_y, "p2"])
            
            elif tipo == "m" and self.player_id == "p2": # Se for o estado de um meteoro e eu for o P2, registro o meteoro que o P1 criou localmente
                mx = data.get("x") 
                mtype = data.get("m_type")
                self.meteors.append([mx, -32, mtype])
                self.meteor_count += 1 
            elif tipo == "game_over_trigger": # Se o outro jogador tiver um game over, o outro também terá.
                self.state = "game_over"

        # Envia um sinal para o servidor a cada 30 frames (1 vez por segundo)
        # PAra evitar que o servidor ache que o jogador desconectou por inatividade, já que ele tem um timeout de 5 segundos
        if pyxel.frame_count % 30 == 0:
            self.network.send_data({"type": "ping", "id": self.player_id})
        # Verifica se o tempo de espera para o outro jogador entrar acabou, se sim, volta para o menu de níveis
        if (self.state == "niveis" or self.state == "aguardando_nivel") and self.waiting_start_time is not None:
            elapsed = (pyxel.frame_count - self.waiting_start_time) // 30
            if elapsed >= self.connection_timeout: 
                self.state = "niveis"
                self.waiting_start_time = None
                self.jogadores_prontos = False

        # 2. LÓGICA DE ESTADOS
        if self.state == "menu":
            self.update_menu()
        elif self.state == "niveis":
            self.level_menu()
        
        # Validação de Nível
        elif self.state == "aguardando_nivel":
            if self.remote_difficulty is not None: # Se já recebi a escolha do outro jogador, verifico se é igual a minha escolha
                if self.difficulty == self.remote_difficulty:
                    self.reset_game()
                    self.state = "play"
                else:
                    self.state = "erro_nivel"
                    
        elif self.state == "play":   
            self.update_game(self.difficulty * 20)
            
        elif self.state in ["game_over", "regras", "erro_nivel"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.remote_difficulty = None # Reseta a escolha para tentar de novo
                self.state = "menu"
    # A função de atualização do menu para cada caso de escolha dos botãos
    def update_menu(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            cx = WIDTH // 2 - 60 #Posição dos botões no eixo x

            if cx <= mx <= cx + 120: # Verifica se o clique foi na região dos botões
                if 180 <= my <= 210: # Botão Play
                    self.reset_game()
                    self.state = "niveis"
                elif 230 <= my <= 260: # Botão Regras
                    self.state = "regras"
                elif 280 <= my <= 310: # Botão Sair
                    pyxel.quit()
        
    def level_menu(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): 
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            cx = WIDTH // 2 - 60
            
            # 1. Verifica clique nos botões de nível (1 a 5)
            for i in range(1, 6):
                y_pos = 110 + (i * 40)
                if cx <= mx <= cx + 120 and y_pos <= my <= y_pos + 30: 
                    self.difficulty = i
                    self.network.send_data({"type": "choose_level", "val": i})
                    self.state = "aguardando_nivel"
                    self.waiting_start_time = pyxel.frame_count 
                    return # Sai da função após detectar o clique

            # 2. Verifica clique no texto "(Clique para voltar)"
            if (WIDTH // 2 - 50 <= mx <= WIDTH // 2 + 50) and (355 <= my <= 375):
                self.state = "menu"
                self.waiting_start_time = None
                self.remote_difficulty = None

    def reset_game(self): # Reinicia o jogo
        self.player1_x = WIDTH // 2 - 40
        self.player2_x = WIDTH // 2 + 10
        self.player_y = HEIGHT - 50
        self.score_p1 = 0
        self.score_p2 = 0
        self.bullets_p1.clear()
        self.bullets_p2.clear()
        self.meteors.clear()
        self.meteor_count = 0
        self.explosions.clear()
        self.difficulty = 1 # Dificuldade inicial

    # Explosão para os meteoros vermelhos, eles destroem outros meteoros em um raio de 150 pixels
    def explode_meteor_special(self, cx, cy, dono):
        for m in self.meteors[:]:
            mx, my, _ = m # Pega a posição do meteoro para calcular a distância da explosão
            dx = mx - cx
            dy = my - cy
            if dx*dx + dy*dy < SPECIAL_RADIUS * SPECIAL_RADIUS: # Se o meteoro estiver dentro do raio de explosão, ele é destruído
                if m in self.meteors: self.meteors.remove(m)
                for _ in range(10):
                    self.explosions.append(Particula(mx + 16, my + 16))
                # Pontua para quem causou a explosão
                if dono == "p1": self.score_p1 += 5
                else: self.score_p2 += 5

    def update_game(self, num_meteors):
        # 1. Movimentação Local dos Jogadores e Envio de Status
        if self.player_id == "p1":
            if pyxel.btn(pyxel.KEY_A): self.player1_x -= 4 # Move para a esquerda
            if pyxel.btn(pyxel.KEY_D): self.player1_x += 4 # Move para a direita
            self.player1_x = max(0, min(WIDTH - 32, self.player1_x)) # Limita o movimento para dentro da tela
            self.network.send_data({"type": "status", "id": "p1", "x": self.player1_x, "score": self.score_p1})
        else:
            if pyxel.btn(pyxel.KEY_LEFT): self.player2_x -= 4
            if pyxel.btn(pyxel.KEY_RIGHT): self.player2_x += 4
            self.player2_x = max(0, min(WIDTH - 32, self.player2_x))
            self.network.send_data({"type": "status", "id": "p2", "x": self.player2_x, "score": self.score_p2})

        # 3. Disparos Locais 
        if self.player_id == "p1" and pyxel.btnp(pyxel.KEY_SPACE):
            self.bullets_p1.append([self.player1_x + 14, self.player_y, "p1"])
            self.network.send_data({"type": "shoot", "id": "p1"})

        if self.player_id == "p2" and (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
            self.bullets_p2.append([self.player2_x + 14, self.player_y, "p2"])
            self.network.send_data({"type": "shoot", "id": "p2"})

        # 2. Processamento de Mensagens de Rede 
        # O receive_data() já retorna um dicionário pronto ou None
        data = self.network.receive_data()
        if data and isinstance(data, dict): 
            tipo = data.get("type")
            
            if tipo == "status":
                if data["id"] == "p1" and self.player_id == "p2":
                    self.player1_x = data["x"]
                    self.score_p1 = data.get("score", self.score_p1)
                elif data["id"] == "p2" and self.player_id == "p1":
                    self.player2_x = data["x"]
                    self.score_p2 = data.get("score", self.score_p2)
            
            elif tipo == "shoot":
                pyxel.play(0, 1) # Som de tiro (banco 1, som 1)
                p_shooter = data.get("id")
                if p_shooter == "p1" and self.player_id == "p2": 
                    self.bullets_p1.append([self.player1_x + 14, self.player_y, "p1"])
                elif p_shooter == "p2" and self.player_id == "p1":
                    self.bullets_p2.append([self.player2_x + 14, self.player_y, "p2"])
            
            elif tipo == "m" and self.player_id == "p2": # Se o P1 criou um meteoro, o P2 cria também localmente
                mx = data.get("x")
                mtype = data.get("m_type")
                self.meteors.append([mx, -32, mtype])
                self.meteor_count += 1


        # 4. Atualização de Balas (Deslocamento e Remoção)
        for b in self.bullets_p1[:]: #Para cada bala do jogador 1, move ela para cima e remove se sair da tela
            b[1] -= 6
            if b[1] < 0: self.bullets_p1.remove(b)
        for b in self.bullets_p2[:]:
            b[1] -= 6
            if b[1] < 0: self.bullets_p2.remove(b)

        # 5. Lógica de Host (Spawn de Meteoros)
        # Apenas P1 decide o nascimento para evitar meteoros duplicados em lugares diferentes
        if self.player_id == "p1":
            if self.meteor_count < num_meteors:
                # A cada 30 frames, há uma chance de spawnar um meteoro, a chance aumenta com a dificuldade
                if pyxel.frame_count % max(1, (30 // self.difficulty)) == 0: 
                    if random.randint(0, 10) > 7: 
                        x = random.randint(0, WIDTH - 32)
                        mtype = "special" if (self.meteor_count + 1) % SPECIAL_EVERY == 0 else "normal"
                        self.meteors.append([x, -32, mtype])
                        self.meteor_count += 1
                        self.network.send_data({"type": "m", "x": x, "m_type": mtype})

        # 6. Movimentação e Colisões (Processamento em Paralelo)
        for m in self.meteors[:]:
            mtype = m[2]
            # Meteoros especiais descem um pouco mais devagar pela dificuldade de serem maiores
            m[1] += (1.5 + self.difficulty * 0.5) if mtype == "special" else (2 + self.difficulty * 0.5)

            if m[1] > HEIGHT: # Se um meteoro passar do limite inferior da tela, o jogo acaba para ambos os jogadores
                self.state = "game_over"
                self.network.send_data({"type": "game_over_trigger"})

            # Checar colisão com todas as balas disponíveis
            for b in self.bullets_p1 + self.bullets_p2:
                mx, my = m[0], m[1]
                # Define a largura e altura do meteoro com base no tipo (especial ou normal)
                mw = 32 if mtype == "special" else 15  
                mh = 16 if mtype == "special" else 15 

                if (mx < b[0] < mx + mw) and (my < b[1] < my + mh):  # Colisão detectada
                    dono = b[2]
                    # Som de explosão para ambos os jogadores
                    pyxel.play(0, 0)
                    # Efeito visual da minha classe Particula
                    for _ in range(10):
                        self.explosions.append(Particula(mx + mw//2, my + mh//2))

                    # Lógica especial
                    # Se for um meteoro especial, ele causa uma explosão que pode destruir outros meteoros próximos, 
                    if mtype == "special": 
                        self.explode_meteor_special(mx + mw//2, my + mh//2, dono)
                    else:  # caso contrário, apenas pontua normalmente
                        if dono == "p1": self.score_p1 += 1
                        else: self.score_p2 += 1

                    # Limpeza
                    if m in self.meteors: self.meteors.remove(m)
                    if b in self.bullets_p1: self.bullets_p1.remove(b)
                    elif b in self.bullets_p2: self.bullets_p2.remove(b)
                    break 

        # 7. Partículas
        for p in self.explosions[:]:
            p.atualizar()
            if p.tdv <= 0: self.explosions.remove(p)

        # 8. Condição de Vitória
        if self.meteor_count >= num_meteors and not self.meteors:
            self.state = "game_over" # O draw_end_screen tratará como vitória          
    
    # Desenha todos os elementos na tela
    def draw(self):
        pyxel.cls(0)

        TILE = 256
        # Como só possui 3 bancos de imagens (0, 1 e 2), e optei por usar apenas um banco de recursos do meu jogo
        # Por isso, desenhei ele como um "mosaico" repetindo a imagem algumas vezes
        # A imagem foi criada com 256x256 pixels no pixart por mim e carregada no banco de imagens 0.
        for y in range(0, HEIGHT, TILE): # Desenha o background como um "mosaico"
            for x in range(0, WIDTH, TILE):
                pyxel.blt(x, y, 0, 0, 0, TILE, TILE)

        if self.state == "menu": # Tela de menu
            text = "DESTRUIDOR DE METEOROS"
            # No Pyxel padrão, cada caractere tem 4 pixels de largura
            text_width = len(text) * 4

            pyxel.text(
                WIDTH // 2 - text_width // 2,
                120,
                text,
                pyxel.COLOR_WHITE
            )
            cx = WIDTH // 2 - 60
            self.draw_button(cx, 180, 120, 30, "Play", pyxel.COLOR_ORANGE)
            self.draw_button(cx, 230, 120, 30, "Regras", pyxel.COLOR_DARK_BLUE)
            self.draw_button(cx, 280, 120, 30, "Sair", pyxel.COLOR_BROWN)
        elif self.state == "aguardando_nivel":
            pyxel.cls(0)
            msg = "AGUARDANDO O OUTRO JOGADOR..."
            msg2 = f"VOCE ESCOLHEU O NIVEL {self.difficulty}"
            pyxel.text(WIDTH // 2 - (len(msg) * 2), HEIGHT // 2 - 10, msg, pyxel.COLOR_YELLOW)
            pyxel.text(WIDTH // 2 - (len(msg2) * 2), HEIGHT // 2 + 10, msg2, pyxel.COLOR_WHITE)
            if self.waiting_start_time is not None:
                elapsed = (pyxel.frame_count - self.waiting_start_time) // 30
                remaining = max(0, self.connection_timeout - elapsed)
                pyxel.text(WIDTH // 2 - 45, 10, f"Tempo limite de espera: {remaining}s", pyxel.COLOR_RED)
            

        elif self.state == "erro_nivel":
            pyxel.cls(0)
            msg = "NIVEIS DIFERENTES DETECTADOS!"
            msg2 = f"Voce: {self.difficulty} | Parceiro: {self.remote_difficulty}"
            msg3 = "COMBINEM O NIVEL E TENTEM NOVAMENTE"
            pyxel.text(WIDTH // 2 - (len(msg) * 2), HEIGHT // 2 - 20, msg, pyxel.COLOR_RED)
            pyxel.text(WIDTH // 2 - (len(msg2) * 2), HEIGHT // 2, msg2, pyxel.COLOR_WHITE)
            pyxel.text(WIDTH // 2 - (len(msg3) * 2), HEIGHT // 2 + 20, msg3, pyxel.COLOR_ORANGE)
            pyxel.text(WIDTH // 2 - 40, HEIGHT // 2 + 60, "(Clique para voltar)", pyxel.COLOR_PURPLE)
        elif self.state == "niveis": # Tela de seleção de níveis
            # Título da tela de seleção
            titulo = "SELECIONE O NIVEL DE DIFICULDADE"
            pyxel.text(WIDTH // 2 - (len(titulo) * 2), 80, titulo, pyxel.COLOR_WHITE) # Centraliza o título
            
            cx = WIDTH // 2 - 60 # Posição X central para os botões
            # Criando 5 botões para cada nível
            for i in range(1, 6):
                # Calcula a posição Y para os botões ficarem um embaixo do outro
                y_pos = 110 + (i * 40)
                self.draw_button(cx, y_pos, 120, 30, f"Nivel {i}", pyxel.COLOR_PURPLE)
            
            pyxel.text(WIDTH // 2 - 40, 360, "(Clique para voltar)", pyxel.COLOR_PURPLE)
            
                        
        elif self.state == "play": # Tela de jogo
            # Desenha a nave do player 1 (amarela e marrom)
            # blt(x, y, banco, u, v, largura, altura, cor_transparente)
            pyxel.blt(self.player1_x, self.player_y, 1, 0, 0, 31, 31, 0)

            # Desenha o Player 2 (Sprite em 40, 0)
            pyxel.blt(self.player2_x, self.player_y, 1, 40, 0, 31, 31, 0)

            for b in self.bullets_p1: # Desenha as balas do player 1
                pyxel.rect(b[0], b[1], 3, 8, pyxel.COLOR_YELLOW)

            for b in self.bullets_p2: # Desenha as balas do player 2
                pyxel.rect(b[0], b[1], 3, 8, pyxel.COLOR_RED)

            for m in self.meteors: # Desenha os meteoros que estão no banco de imagens 2
                x, y, mtype = m

                if mtype == "special": # meteoro vermelho
                    # Desenha o meteoro especial (vermelho)
                    pyxel.blt(x, y, 2, 32, 0, 32, 16, 0)

                else:
                    # meteoro normal
                    pyxel.blt(x, y, 2, 0, 0, 15, 15, 0)

            for p in self.explosions: # Desenha as partículas de explosão
                p.desenhar()
            
            # Desenha a pontuação do jogador
            pyxel.rect(5, 5, 80, 20, pyxel.COLOR_BLACK)
            pyxel.text(10, 10, f"Player 1: {self.score_p1}", pyxel.COLOR_WHITE)
            
            pyxel.rect(WIDTH - 85, 5, 80, 20, pyxel.COLOR_BLACK)
            pyxel.text(WIDTH - 80, 10, f"Player 2: {self.score_p2}", pyxel.COLOR_CYAN)
        
        elif self.state == "game_over": # Tela de fim de jogo
            self.draw_end_screen()
        elif self.state == "regras": # Tela de regras do jogo
            pyxel.text(90, 140,
                "UMA ENORME CHUVA DE METEOROS ESTA INDO PARA A TERRA,\n\n"
                "DESTRUA TODOS ELES ANTES QUE CHEGUEM LA!!\n",
                pyxel.COLOR_GRAY
            )

            pyxel.text(90, 200,
                "-----REGRAS DO JOGO-----\n\n\n"
                "# METEOROS NORMAIS:\n\n"
                "  - VALEM 1 PONTO CADA.\n\n"
                "# METEOROS VERMELHOS:\n\n"
                "  - VALEM 5 PONTOS CADA.\n"
                "  - AO SEREM DESTRUIDOS GERAM UMA EXPLOSAO\n"
                "   QUE DESTRÓI OUTROS METEOROS NUM RAIO DE 150 PIXELS.\n\n\n"
                "# O JOGO ACABA SE UM METEORO PASSAR DO LIMITE INFERIOR DA TELA.\n\n"
                "# JOGADOR 1 (AMAREMO E MARROM): TECLA A (ESQUERDA), D (DIREITA) E SPACE (TIRO)\n\n"
                "# JOGADOR 2 (ROSA E ROXO): SETA ESQUERDA, SETA DIREITA E ENTER (OU CLIQUE COM \nO MOUSE) PARA ATIRAR\n\n\n",                
                pyxel.COLOR_GRAY
            )

            pyxel.text(160, 360, "(Clique para voltar)", pyxel.COLOR_PURPLE)

    def draw_button(self, x, y, w, h, text, color): # Desenha botões interativos
        if x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h:
            color = 12
        pyxel.rect(x, y, w, h, color)
        tx = x + (w - len(text) * 4) // 2
        pyxel.text(tx, y + h//2 - 2, text, pyxel.COLOR_WHITE)
    def draw_end_screen(self):
        pyxel.cls(0)
        # Se não houver meteoros na lista, significa que ele destruiu todos
        if len(self.meteors) == 0 and self.meteor_count >= (self.difficulty * 5):
            msg = "MISSAO CUMPRIDA!"
            cor = pyxel.COLOR_LIME
        else:
            msg = "GAME OVER"
            cor = pyxel.COLOR_RED
            
        pyxel.text(WIDTH // 2 - (len(msg) * 2), HEIGHT // 2 - 10, msg, cor)
        pyxel.text(WIDTH // 2 - 30, HEIGHT // 2 + 10, "SCORE", pyxel.COLOR_WHITE)
        pyxel.text(WIDTH // 2 - 30, HEIGHT // 2 + 20, f"Player 1: {self.score_p1}", pyxel.COLOR_WHITE)
        pyxel.text(WIDTH // 2 - 30, HEIGHT // 2 + 30, f"Player 2: {self.score_p2}", pyxel.COLOR_WHITE)
        
        cx = WIDTH // 2 - 60
        self.draw_button(cx, 280, 120, 30, "Voltar ao menu", pyxel.COLOR_BROWN)
    
if __name__ == "__main__":
    Game()
