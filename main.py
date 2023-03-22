#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os.path import abspath, dirname
from random import choice, uniform
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import *
#PARÁMETROS:
CATS_COLUMNS = 10           #Cantidad de columnas.
CATS_ROWS = 4               #Cantidad de filas.          
CATS_LENGTH = [70, 70]      #Tamaño (x,y).
CATS_TOP = 80               #Posición vertical grupo (top).
CATS_SEPARATION=[10, 10]    #Separación entre gatos (x,y).
CATS_UPDATE_TIME = 600      #Intervalo de actualización.
CATS_VELOCITY = 10          #Velocidad de bloque.
CATS_SHOOT_TIME = 800       #Frecuencia de dardos.
CATS_MOVE_DOWN = 35         #Desplazamiento vertical.
CATS_DART_MULTIPLIER = 2    #Multiplicador de dificultad por nivel.
ANTO_LENGTH=[120, 100]      #Tamaño (x,y).
ANTO_BOTTOM = 10            #Holgura inferior.
ANTO_SPEED = 15             #Velocidad horizontal.
ANTO_LIVES = 3              #Cantidad de vidas.
DART_LENGTH = [10, 30]      #Tamaño (x,y).
DART_SPEED = [20, 10]       #Velocidad (Anto,gatos).
SAND_BLOCKS = 5             #Cantidad de bloques.
SAND_COLUMNS = 10           #Cantidad de columnas.
SAND_ROWS = 3               #Cantidad de filas.
SAND_LENGTH = [15, 15]      #Tamaño (x,y).
SAND_POSITION = 500         #Comienzo estructuras (top).
YUKI_LENGTH = [70, 50]      #Tamaño (x,y).
YUKI_MID = 50               #Posición vertical (mid).
YUKI_SPEED = 15             #Velocidad horizontal.
YUKI_INTERVAL = 5000        #Frecuencia media de aparición (dist. uniforme).
LIFE_LENGTH = [25, 25]      #Tamaño vidas (x,y).
LATERAL_LIMIT = 10          #Limite lateral.
RESOLUTION = (1200, 700)    #Resolución pantalla.
NEW_ROUND_TIME = 3000       #Tiempo mensaje nivel.
SCORE_2DART = 5000          #Puntaje mínimo para doble flecha.
#CONSTANTES:
PATH = abspath(dirname(__file__))
SCREEN = display.set_mode(RESOLUTION)
IMAGES = {name: image.load(PATH + '/images/' + name + '.png').convert_alpha()
        for name in ['anto',
                    'yuki', 'cat0', 'cat1', 'cat2', 'cat3', 'cat4',
                    'heart', 'dart1', 'dart-1', 'sand',
                    'bgmain', 'bggame', 'bggameover', 'cat_main',
                    'icon']}
FONT_YUKI_SCORE = PATH + '/fonts/Courier New Bold.ttf'
FONT_MAIN = PATH + '/fonts/Phosphate.ttc'
FONT_BEGIN = PATH + '/fonts/Copperplate.ttc'
FONT_ANIVERSARIO = PATH + '/fonts/SnellRoundhand.ttc'
CATS_LATERAL_FREE = (RESOLUTION[0] - CATS_COLUMNS * CATS_LENGTH[0] - (CATS_COLUMNS - 1) * CATS_SEPARATION[0]) / 2
SAND_SEPARATION = (RESOLUTION[0] - 2 * LATERAL_LIMIT - SAND_BLOCKS * SAND_COLUMNS * SAND_LENGTH[0]) / (SAND_BLOCKS + 1)
CATS_FREE_MOVES = (CATS_LATERAL_FREE - LATERAL_LIMIT) / CATS_VELOCITY
COLUMN4MOVE = (CATS_LENGTH[0] + CATS_SEPARATION[0]) / CATS_VELOCITY
class Anto(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(IMAGES['anto'], ANTO_LENGTH)
        self.rect = self.image.get_rect(midbottom = (RESOLUTION[0] / 2, RESOLUTION[1] - ANTO_BOTTOM))
    def update(self, keys, *args):
        if keys[K_LEFT]:
            if self.rect.left - ANTO_SPEED >= LATERAL_LIMIT: self.rect.x -= ANTO_SPEED
            else: self.rect.left = LATERAL_LIMIT
        if keys[K_RIGHT]:
            if self.rect.right + ANTO_SPEED <= RESOLUTION[0] - LATERAL_LIMIT: self.rect.x += ANTO_SPEED
            else: self.rect.right = RESOLUTION[0] - LATERAL_LIMIT
        game.screen.blit(self.image, self.rect)
class Dart(sprite.Sprite):
    def __init__(self, x, y, direction):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(IMAGES['dart' + str(direction)], DART_LENGTH)
        self.rect = self.image.get_rect(midtop = (x, y))
        self.direction = direction
    def update(self, keys, *args):
        self.rect.y += self.direction * DART_SPEED[int(1 / 2.0 + self.direction / 2.0)]
        if self.rect.top <= YUKI_MID or self.rect.bottom >= RESOLUTION[1] - ANTO_BOTTOM: self.kill()
        game.screen.blit(self.image, self.rect)
class Cat(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.image = transform.scale(IMAGES['cat' + str(self.row)], CATS_LENGTH)
        self.rect = self.image.get_rect()
    def update(self, *args):
        game.screen.blit(self.image, self.rect)
class CatsGroup(sprite.Group):
    def __init__(self,columns,rows):
        sprite.Group.__init__(self)
        self.cats = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.direction = 1
        self.rightMoves = CATS_FREE_MOVES
        self.leftMoves = CATS_FREE_MOVES
        self.moveNumber = CATS_FREE_MOVES / 2 + 1
        self.timer = time.get_ticks()
        self.bottom = 0
        self.aliveColumns = list(range(columns))
        self.leftAliveColumn = 0
        self.rightAliveColumn = columns - 1
    def update(self, current_time):
        if current_time - self.timer >= CATS_UPDATE_TIME:
            if self.direction == 1: max_move = self.rightMoves + self.rightAddMove
            else: max_move = self.leftMoves + self.leftAddMove
            if self.moveNumber >= max_move:
                self.leftMoves = CATS_FREE_MOVES + self.rightAddMove
                self.rightMoves = CATS_FREE_MOVES + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for cat in self:
                    cat.rect.y += CATS_MOVE_DOWN
                    if self.bottom < cat.rect.y + CATS_LENGTH[1]: self.bottom = cat.rect.y + CATS_LENGTH[1]
            else:
                for cat in self: cat.rect.x += self.direction * CATS_VELOCITY
                self.moveNumber += 1
            self.timer += CATS_UPDATE_TIME
    def add_internal(self, *sprites):
        super(CatsGroup, self).add_internal(*sprites)
        for s in sprites: self.cats[s.row][s.column] = s 
    def remove_internal(self, *sprites):
        super(CatsGroup, self).remove_internal(*sprites)
        for s in sprites: self.kill(s)    
    def is_column_dead(self, column):
        return not any(self.cats[row][column] for row in range(self.rows))
    def random_bottom(self):
        col = choice(self.aliveColumns)
        col_cats = (self.cats[row - 1][col] for row in range(self.rows, 0, -1))
        return next((en for en in col_cats if en is not None), None)
    def kill(self, cat):
        self.cats[cat.row][cat.column] = None
        is_column_dead = self.is_column_dead(cat.column)
        if is_column_dead: self.aliveColumns.remove(cat.column)
        if cat.column == self.rightAliveColumn:
            while self.rightAliveColumn > 0 and is_column_dead:
                self.rightAliveColumn -= 1
                self.rightAddMove += COLUMN4MOVE
                is_column_dead = self.is_column_dead(self.rightAliveColumn)
        elif cat.column == self.leftAliveColumn:
            while self.leftAliveColumn < self.columns and is_column_dead:
                self.leftAliveColumn += 1
                self.leftAddMove += COLUMN4MOVE
                is_column_dead = self.is_column_dead(self.leftAliveColumn)
class Sand(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.image = transform.scale(IMAGES['sand'], SAND_LENGTH)
        self.rect = self.image.get_rect()
    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
class Yuki(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(IMAGES['yuki'], YUKI_LENGTH)
        self.image_flipped = transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midright = (0, YUKI_MID))
        self.direction = 1
        self.oscilation = 1
        self.timer = time.get_ticks()
    def update(self, keys, currentTime, *args):
        resetTimer = False
        if currentTime - self.timer >= YUKI_INTERVAL * self.oscilation:
            if self.rect.left < RESOLUTION[0] and self.direction == 1: self.rect.x += YUKI_SPEED
            if self.rect.right > 0 and self.direction == -1: self.rect.x -= YUKI_SPEED
            if self.direction == 1: game.screen.blit(self.image, self.rect)
            else: game.screen.blit(self.image_flipped, self.rect)
        if self.rect.left >= RESOLUTION[0]:
            self.direction = -1
            resetTimer = True
        if self.rect.right <= 0:
            self.direction = 1
            resetTimer = True
        if currentTime - self.timer > YUKI_INTERVAL * self.oscilation and resetTimer:
            self.timer = currentTime
            self.oscilation = uniform(1, 2)
class CatTouch(sprite.Sprite):
    def __init__(self, cat, *groups):
        super(CatTouch, self).__init__(*groups)
        self.image = transform.scale(IMAGES['heart'], CATS_LENGTH)
        self.rect = self.image.get_rect(topleft = (cat.rect.x, cat.rect.y))
        self.timer = time.get_ticks()
    def update(self, current_time, *args):
        if current_time - self.timer > 100: self.kill()
        game.screen.blit(self.image, self.rect)
class YukiTouch(sprite.Sprite):
    def __init__(self, yuki, score, *groups):
        super(YukiTouch, self).__init__(*groups)
        self.text = Text(FONT_YUKI_SCORE, 20, str(score), (255, 255, 255), (yuki.rect.x + 20, yuki.rect.y + 6))
        self.timer = time.get_ticks()
    def update(self, current_time, *args):
        if current_time - self.timer <= 600: self.text.draw(game.screen)
        else: self.kill()
class AntoTouch(sprite.Sprite):
    def __init__(self, anto, *groups):
        super(AntoTouch, self).__init__(*groups)
        self.image = transform.scale(IMAGES['anto'], ANTO_LENGTH)
        self.rect = self.image.get_rect(topleft = (anto.rect.x, anto.rect.y))
        self.timer = time.get_ticks()
    def update(self, current_time, *args):
        if 300 <= current_time - self.timer <= 600: game.screen.blit(self.image, self.rect)
        elif 900 < current_time - self.timer: self.kill()
class Life(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(IMAGES['anto'], LIFE_LENGTH)
        self.rect = self.image.get_rect(center = (x,y))
    def update(self, *args):
        game.screen.blit(self.image, self.rect)
class Text(object):
    def __init__(self, textFont, size, message, color, position):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(center = position)
    def draw(self, surface):
        surface.blit(self.surface, self.rect)
class Anniversary(object):
    def __init__(self):
        init()
        self.icon = transform.scale(IMAGES['icon'], (256, 256))
        self.set_icon(self.icon)
        self.clock = time.Clock()
        self.multiplier = 1
        self.caption = display.set_caption('Amor a los gatitos')
        self.screen = SCREEN
        self.background = transform.scale(IMAGES['bgmain'], RESOLUTION)
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        self.catPosition = CATS_TOP
        self.TextTitle = Text(FONT_MAIN, 70, 'Amor a los gatitos', (253, 253, 238), (RESOLUTION[0] / 2 + 100, RESOLUTION[1] / 2))
        self.TextBegin = Text(FONT_BEGIN, 25, 'Presiona una tecla para continuar', (255, 255, 255), (RESOLUTION[0] / 2, RESOLUTION[1] - 50))
        self.gameOverText = Text(FONT_MAIN, 80, 'Game Over', (255, 255, 255), (RESOLUTION[0] / 2, RESOLUTION[1] / 2))
        self.nextRoundText = Text(FONT_MAIN, 50, 'Siguiente nivel', (100, 120, 100), (RESOLUTION[0] / 2, RESOLUTION[1] / 2))
        self.AniversarioText = Text(FONT_ANIVERSARIO, 40, 'Feliz aniversario', (255,255,255), (RESOLUTION[0] / 2  , RESOLUTION[1] /2 - 40))
        self.scoreText = Text(FONT_MAIN, 20, 'Amor', (255, 255, 255), (50, 20))
        self.livesText = Text(FONT_MAIN, 20, 'Vidas', (255, 255, 255), (RESOLUTION[0] - 3 * (LIFE_LENGTH[0] + 10) - 50, 20))
        self.life = [Life(RESOLUTION[0] - i * (LIFE_LENGTH[0] + 10) - 30, 20) for i in range(ANTO_LIVES)]
        self.livesGroup = sprite.Group(self.life[i] for i in range(ANTO_LIVES))
    def set_icon(self, app_icon):
        icon = Surface((256, 256))
        icon.set_colorkey((0, 0, 0))
        for i in range(0, 256):
            for j in range(0, 256): icon.set_at((i, j), app_icon.get_at((i, j)))
        display.set_icon(icon)
    def reset(self, score):
        self.player = Anto()
        self.playerGroup = sprite.Group(self.player)
        self.touchsGroup = sprite.Group()
        self.darts = sprite.Group()
        self.guagua = Yuki()
        self.yukiGroup = sprite.Group(self.guagua)
        self.catDarts = sprite.Group()
        self.make_cats()
        self.allSprites = sprite.Group(self.player, self.cats, self.livesGroup, self.guagua)
        self.keys = key.get_pressed()
        self.timer = time.get_ticks()
        self.antoTimer = time.get_ticks()
        self.score = score
        self.makeNewAnto = False
        self.antoAlive = True
    def make_sand_block(self, block_number):
        sandGroup = sprite.Group()
        for row in range(SAND_ROWS):
            for column in range(SAND_COLUMNS):
                sand = Sand(row, column)
                sand.rect.x = LATERAL_LIMIT + block_number * SAND_COLUMNS * SAND_LENGTH[0] + (block_number + 1) * SAND_SEPARATION + column * SAND_LENGTH[0]
                sand.rect.y = SAND_POSITION + (row * SAND_LENGTH[1])
                sandGroup.add(sand)
        return sandGroup
    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if e.type == QUIT: exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.darts) == 0 and self.antoAlive:
                        if self.score < SCORE_2DART:
                            dart = Dart(self.player.rect.centerx, self.player.rect.y, -1)
                            self.darts.add(dart)
                            self.allSprites.add(self.darts)
                        else:
                            leftdart = Dart(self.player.rect.centerx -ANTO_LENGTH[0] / 5, self.player.rect.y, -1)
                            rightdart = Dart(self.player.rect.centerx +ANTO_LENGTH[0] / 5, self.player.rect.y, -1)
                            self.darts.add(leftdart)
                            self.darts.add(rightdart)
                            self.allSprites.add(self.darts)       
    def make_cats(self):
        cats = CatsGroup(CATS_COLUMNS, CATS_ROWS)
        for row in range(CATS_ROWS):
            for column in range(CATS_COLUMNS):
                cat = Cat(row, column)
                cat.rect.x = CATS_LATERAL_FREE + (CATS_SEPARATION[0] + 1) * column + column * CATS_LENGTH[0]
                cat.rect.y = CATS_TOP + row * (CATS_LENGTH[1] + CATS_SEPARATION[1])
                cats.add(cat)
        self.cats = cats
    def make_cats_shoot(self,multiplier):
        if (time.get_ticks() - self.timer) >= CATS_SHOOT_TIME / multiplier:
            cat = self.cats.random_bottom()
            self.catDarts.add(Dart(cat.rect.centerx, cat.rect.centery, 1))
            self.allSprites.add(self.catDarts)
            self.timer = time.get_ticks()
    def calculate_score(self, row):
        scores = {i : 100 * (CATS_ROWS - i) for i in range(CATS_ROWS)}
        scores[CATS_ROWS] = choice([500 * (i + 1) for i in range(10)])
        score = scores[row]
        self.score += score
        return score
    def check_collisions(self):
        sprite.groupcollide(self.darts, self.catDarts, True, True)
        for cat in sprite.groupcollide(self.cats, self.darts,True, True).keys():
            self.calculate_score(cat.row)
            CatTouch(cat, self.touchsGroup)
            self.gameTimer = time.get_ticks()
        for yuki in sprite.groupcollide(self.yukiGroup, self.darts,True, True).keys():
            score = self.calculate_score(CATS_ROWS)
            YukiTouch(yuki, score, self.touchsGroup)
            newYuki = Yuki()
            self.allSprites.add(newYuki)
            self.yukiGroup.add(newYuki)
        for player in sprite.groupcollide(self.playerGroup, self.catDarts,True, True).keys():
            for i in range(ANTO_LIVES):
                if i + 1 == ANTO_LIVES:
                    self.gameOver = True
                    self.startGame = False
                elif self.life[i].alive():
                    self.life[i].kill()
                    break
            AntoTouch(player, self.touchsGroup)
            self.makeNewAnto = True
            self.antoTimer = time.get_ticks()
            self.antoAlive = False
        if self.cats.bottom >= self.player.rect.top:
            self.gameOver = True
            self.startGame = False
        sprite.groupcollide(self.darts, self.allSand, True, True)
        sprite.groupcollide(self.catDarts, self.allSand, True, True)
        sprite.groupcollide(self.cats, self.allSand, False, True) 
    def create_new_anto(self, createAnto, currentTime):
        if createAnto and (currentTime - self.antoTimer > 900):
            self.player = Anto()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewAnto = False
            self.antoAlive = True
    def create_game_over(self, currentTime):
        self.background = transform.scale(IMAGES['bggameover'], RESOLUTION)
        self.screen.blit(self.background, (0, 0))
        if currentTime - self.timer <= 2500 or (3500 < currentTime - self.timer < 5000): self.gameOverText.draw(self.screen)
        elif currentTime - self.timer > 6000: self.mainScreen = True
        for e in event.get():
            if e.type == QUIT: exit()
    def main(self):
        while True:
            if self.mainScreen:
                self.background = transform.scale(IMAGES['bgmain'], RESOLUTION)
                self.screen.blit(self.background, (0, 0))
                self.TextTitle.draw(self.screen)
                cat_main = transform.scale(IMAGES['cat_main'], (200,200))
                self.screen.blit(cat_main,(RESOLUTION[0] / 2 + 150, RESOLUTION[1] / 2 - 190))
                self.TextBegin.draw(self.screen)
                self.AniversarioText.draw(self.screen)
                for e in event.get():
                    if e.type == QUIT: exit()
                    if e.type == KEYUP:
                        self.allSand = sprite.Group()
                        for i in range(SAND_BLOCKS): self.allSand.add(self.make_sand_block(i))
                        self.livesGroup.add(self.life[i] for i in range(ANTO_LIVES))
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False
            elif self.startGame:
                self.background = transform.scale(IMAGES['bggame'], RESOLUTION)
                if not self.cats and not self.touchsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer <= NEW_ROUND_TIME:
                        self.screen.blit(self.background, (0, 0))
                        self.nextRoundText.draw(self.screen)
                        self.check_input()
                    if currentTime - self.gameTimer >= NEW_ROUND_TIME:
                        self.multiplier *= CATS_DART_MULTIPLIER
                        self.reset(self.score)
                        self.gameTimer += NEW_ROUND_TIME
                else:
                    currentTime = time.get_ticks()
                    self.screen.blit(self.background, (0, 0))
                    self.allSand.update(self.screen)
                    self.scoreTextNumber = Text(FONT_MAIN, 20, str(self.score), (78, 255, 87), (120, 20))
                    self.scoreText.draw(self.screen)
                    self.scoreTextNumber.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.cats.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.touchsGroup.update(currentTime)
                    self.check_collisions()
                    self.create_new_anto(self.makeNewAnto, currentTime)
                    self.make_cats_shoot(self.multiplier)
            elif self.gameOver:
                currentTime = time.get_ticks()
                self.catPosition = CATS_TOP
                self.create_game_over(currentTime)
            display.update()
            self.clock.tick(60)
if __name__ == '__main__':
    game = Anniversary()
    game.main()