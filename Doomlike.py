import pygame
import random


class Game():  # Classe principal
    def __init__(self, screen):
        # Definições da tela
        self.screen = screen
        self.scr_width = self.screen.get_rect().width
        self.scr_height = self.screen.get_rect().height

        # Carregar fonte
        font = 'fonts/AmazDooMLeft.ttf'
        font_size = 60
        self.font = pygame.font.Font(font, font_size)

        # Carregar Audio
        pygame.mixer.music.load('sounds/music0.ogg')
        self.shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
        self.player_death = pygame.mixer.Sound('sounds/PlayerDeath.wav')
        self.player_hurt = pygame.mixer.Sound('sounds/PlayerHurt.wav')

        # Carregar imagem de fundo
        self.background = pygame.image.load('bg.jpg')
        self.bg_size = self.background.get_width()

    def drawCounter(self):  # Desenha o contador de mortes
        text = 'Kills: ' + str(self.counter)
        text = self.font.render(text, True, (250, 250, 250))

        t_w = text.get_rect().width

        self.screen.blit(text, (self.scr_width / 2 - t_w / 2, 20))

    def checkEvents(self):  # Eventos de input
        global mainloop

        pressed = pygame.key.get_pressed()
        # Movimentação lateral
        if pressed[pygame.K_d]:
            for shoot in self.shootList:
                shoot.refreshX(-10)
            for enemy in self.enemyList:
                enemy.refreshX(-10)
            self.bg_pos[0] -= 10
        if pressed[pygame.K_a]:
            for shoot in self.shootList:
                shoot.refreshX(10)
            for enemy in self.enemyList:
                enemy.refreshX(10)
            self.bg_pos[0] += 10

        # Fix da posição do background
        if self.bg_pos[0] == -2650:
            self.bg_pos[0] = 0
        elif self.bg_pos[0] == 800:
            self.bg_pos[0] = -1880

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                # Tiros
                if event.key == pygame.K_SPACE:
                    if self.shoot is False:
                        self.shoot_sound.play(0)
                        self.shoot = True
                        self.shootList.append(Shoot(self.screen))

    def blitChar(self, player):  # Printa a mão do personagem na tela
        player_size = player.sprites[player.currsprite].get_rect().width / 2

        if self.shoot is True:
            self.shoot = player.shootAnim()

        self.screen.blit(
            player.sprites[player.currsprite], (self.scr_width / 2 - player_size, self.scr_height - player.sprites[player.currsprite].get_height()))

    def drawLifes(self, player):  # Printa as faces e a quantidade de vidas do personagem
        text = 'Lifes: ' + str(player.life)
        text = self.font.render(text, True, (250, 250, 250))
        img = pygame.transform.scale(
            player.faces[4 - (player.life - 1)], (player.faces[4 - (player.life - 1)].get_width() * 3, player.faces[4 - (player.life - 1)].get_height() * 3))
        self.screen.blit(img, (10, 500))
        self.screen.blit(text, (100, 530))

    def run(self):

        while True:  # Loop principal
            global mainloop
            mainloop = True
            self.counter = 0
            self.shoot = False
            self.bg_pos = [0, 0]
            self.shootList = []
            self.enemyList = []
            pygame.mixer.music.play(-1)
            player = Player()
            while mainloop:  # Loop da partida

                # Printa o background
                self.screen.blit(self.background, self.bg_pos)

                if self.bg_pos[0] < -1950:
                    self.screen.blit(
                        self.background, (self.bg_pos[0] + 1880 + self.scr_width, self.bg_pos[1]))
                elif self.bg_pos[0] > 0:
                    self.screen.blit(
                        self.background, (self.bg_pos[0] - 2685, self.bg_pos[1]))

                self.checkEvents()

                # Printa os Tiros
                for index, shoot in enumerate(self.shootList):
                    shoot.refresh()
                    self.screen.blit(shoot.img, (shoot.pos_x - 10 + int(shoot.Orig_img.get_width() / 2 - shoot.img.get_width() / 2),
                                                 self.scr_height / 2 + 20 - int(shoot.pos_z / 10)))

                    if shoot.pos_z >= self.scr_height / 2:
                        self.shootList.pop(index)

                # Gera inimigos
                if random.randint(0, 2000) > 1990:
                    self.enemyList.append(Enemy(self.screen))

                # Verifica colisão entre Shoot() e Enemy()
                for enemy_index, enemy in enumerate(self.enemyList):
                    for shoot_index, shoot in enumerate(self.shootList):

                        enemy_dist = abs(enemy.pos_z) / 1000
                        shoot_dist = abs(shoot.pos_z) / 240

                        if enemy.rect.colliderect(shoot.rect) and abs(enemy_dist - shoot_dist) < 0.1:
                            self.shootList.pop(shoot_index)
                            enemy.pain.play(0)
                            enemy.life -= 1
                            enemy.hit = True
                            enemy.hittimer = 0
                            if enemy.life == 0:
                                enemy.death_sound[random.randint(0, 1)].play(0)
                                enemy.deadAnim()
                    if enemy.dead is True:
                        self.counter += 1
                        self.enemyList.pop(enemy_index)

                # Printa os inimigos
                if len(self.enemyList) > 0:
                    for enemy in reversed(self.enemyList):
                        enemy.refresh()
                        self.screen.blit(enemy.img, (enemy.pos_x - 10 + int(enemy.Orig_imgs[0].get_width() / 2 - enemy.img.get_width() / 2),
                                                     self.scr_height / 2 - 90 - int(enemy.pos_z / 20)))

                    # Dano no personagem baseado na pos_z do inimigo
                    for enemy in self.enemyList:
                        if enemy.pos_z < -1000:
                            if enemy.exploding is False:
                                enemy.explo_sound.play(0)
                                enemy.exploding = True
                                enemy.currsprite = 0
                                self.player_hurt.play(0)
                                player.life -= 1

                # Chama as funções de printar
                self.blitChar(player)
                self.drawCounter()
                self.drawLifes(player)

                pygame.display.flip()

                # Verifica se o personagem está vivo
                if player.life <= 0:
                    self.player_death.play(0)
                    mainloop = False


class Shoot():  # Classe do tiro
    def __init__(self, screen):  # Inicia a classe

        self.screen = screen

        self.Orig_img = pygame.image.load('shoot.png')
        self.Orig_img = pygame.transform.scale(
            self.Orig_img, (self.Orig_img.get_width() * 3, self.Orig_img.get_height() * 3))

        self.timer = 0
        self.pos_z = 0
        self.pos_x = screen.get_width() / 2

        self.rect = pygame.Rect(self.pos_x, self.pos_x, 10, 10)

    def refreshX(self, add):  # Atualiza sua posição em X
        self.pos_x += add

    def refresh(self):  # Atualiza sua posição em Z

        size = self.pos_z / 5

        self.img = pygame.transform.scale(
            self.Orig_img, (int(self.Orig_img.get_width() - size), int(self.Orig_img.get_height() - size)))

        self.rect = pygame.Rect(self.pos_x - 10 + int(self.Orig_img.get_width() / 2 - self.img.get_width() / 2),
                                self.screen.get_rect().height / 2 + 20 - int(self.pos_z / 10), self.img.get_width(), self.img.get_height())

        self.timer = (self.timer + 1) % 5
        if self.timer == 0:
            self.pos_z += 60


class Enemy():  # Classe de inimigos
    def __init__(self, screen):  # Inicializa a classe
        self.screen = screen

        self.Orig_imgs = []
        self.Hit_imgs = []
        self.Orig_death = []
        self.Orig_explo = []

        self.hit = False
        self.isAlive = True

        self.currsprite = 0
        self.life = 3

        # Carrega os sprites
        for i in range(5):
            self.Orig_imgs.append(pygame.image.load(
                'enemy/enemy' + str(i) + '.png'))

        for i in range(5):
            self.Hit_imgs.append(pygame.image.load(
                'enemy/enemyhit' + str(i) + '.png'))

        for i in range(10):
            self.Orig_death.append(pygame.image.load(
                'enemy/death' + str(i) + '.png'))

        for i in range(5):
            self.Orig_explo.append(pygame.image.load(
                'enemy/explosion' + str(i) + '.png'))

        # Carrega os sons
        self.explo_sound = pygame.mixer.Sound('sounds/explosion.wav')
        self.pain = pygame.mixer.Sound('sounds/ImpPain.wav')
        self.roam_sound = pygame.mixer.Sound('sounds/ImpRoam.wav')
        self.death_sound = [pygame.mixer.Sound('sounds/ImpDeath1.wav'),
                            pygame.mixer.Sound('sounds/ImpDeath2.wav')]

        self.roam_sound.play(0)

        # Definição de variáveis
        self.pos_z = 100
        self.pos_x = random.randint(100, 700)
        self.timer = 0
        self.rect = pygame.Rect(self.pos_x, self.pos_x, 10, 10)

        # Flags
        self.dying = False
        self.exploding = False
        self.dead = False

    def refreshX(self, add):  # Atualiza posição em X
        self.pos_x += add

    def deadAnim(self):  # Ativa animação de morte
        self.dying = True
        self.currsprite = 0

    def refresh(self):  # Atualiza posição em Z e as sprites para cada flag
        if self.dying:  # Morrendo
            size = self.pos_z / 5
            self.img = pygame.transform.scale(
                self.Orig_death[self.currsprite], (int(self.Orig_death[0].get_width() - size), int(self.Orig_death[0].get_height() - size)))

            self.rect = pygame.Rect(self.pos_x - 10 + int(self.Orig_death[0].get_width() / 2 - self.img.get_width() / 4),
                                    self.screen.get_rect().height / 4 - int(self.pos_z / 20) + 110, self.img.get_width() / 2, self.img.get_height() / 2)

            self.timer = (self.timer + 1) % 5
            if self.timer == 0:
                self.currsprite += 1
                if self.currsprite == len(self.Orig_death):
                    self.dead = True

        elif self.exploding:  # Explodindo
            size = self.pos_z / 5

            self.img = pygame.transform.scale(
                self.Orig_explo[self.currsprite], (int(self.Orig_explo[0].get_width() - size) * 2, int(self.Orig_explo[0].get_height() - size) * 2))

            self.rect = pygame.Rect(self.pos_x - 10 + int(self.Orig_explo[0].get_width() / 2 - self.img.get_width() / 4),
                                    self.screen.get_rect().height / 4 - int(self.pos_z / 20) + 110, self.img.get_width() / 2, self.img.get_height() / 2)

            self.timer = (self.timer + 1) % 5
            if self.timer == 0:
                self.currsprite += 1
                if self.currsprite == len(self.Orig_explo):
                    self.dead = True
        else:  # Andando normal
            size = self.pos_z / 5

            if self.hit:
                self.img = pygame.transform.scale(
                    self.Hit_imgs[self.currsprite], (int(self.Hit_imgs[0].get_width() - size), int(self.Hit_imgs[0].get_height() - size)))
            else:
                self.img = pygame.transform.scale(
                    self.Orig_imgs[self.currsprite], (int(self.Orig_imgs[0].get_width() - size), int(self.Orig_imgs[0].get_height() - size)))

            self.rect = pygame.Rect(self.pos_x - 10 + int(self.Orig_imgs[0].get_width() / 2 - self.img.get_width() / 4),
                                    self.screen.get_rect().height / 4 - int(self.pos_z / 20) + 110, self.img.get_width() / 2, self.img.get_height() / 2)

            self.timer = (self.timer + 1) % 5
            if self.timer == 0:
                self.currsprite += 1
                self.currsprite = self.currsprite % 5
                self.pos_z -= 10

            if self.hit:
                self.hittimer = (self.hittimer + 1) % 15
                if self.hittimer == 0:
                    self.hit = False


class Player():  # Classe do jogador
    def __init__(self):

        # Carrega imagens
        self.sprites = []
        for img in range(3):
            self.sprites.append(pygame.image.load(
                'hand0' + str(img + 1) + '.png'))

        for index, img in enumerate(self.sprites):
            self.sprites[index] = pygame.transform.scale(
                img, (img.get_width() * 3, img.get_height() * 3))

        self.faces = []
        for img in range(6):
            self.faces.append(pygame.image.load(
                'faces/face' + str(img) + '.png'))

        # Define variáveis
        self.life = 5
        self.currsprite = 0
        self.timer = 0

    def shootAnim(self):  # Gerencia animação de tiro
        self.timer = (self.timer + 1) % 8
        if self.timer == 0:
            self.currsprite = (self.currsprite + 1) % 3
            if self.currsprite == 0:
                return (False)
        return(True)


# Inicializa pygame e mixer
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

# Roda o programa
if __name__ == "__main__":
    # Cria a tela
    clock = pygame.time.Clock()
    clock.tick(30)

    screen = pygame.display.set_mode((800, 600), 0, 32)
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Doomlike')

    # Roda a classe Game()
    Game = Game(screen)
    Game.run()
