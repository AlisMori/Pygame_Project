import pygame
from random import randrange as rnd
import sys
import os
import random


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


money = 0


def start_screen():  # Заставка
    WIDTH, HEIGHT = 900, 650
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    intro_text = ["Правила игры",
                  "В этой игре Вам необходимо уничтожить все блоки так, чтобы мячик не упал.",
                  "Перемещение платформы с помощью клавиш вперед и назад."]

    fon = pygame.transform.scale(load_image('1.jpg'), (WIDTH // 2, HEIGHT // 2))
    screen.blit(fon, (200, 200))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                play_game(money)
        pygame.display.flip()
        clock.tick(50)


def end_screen(flag, money):
    WIDTH, HEIGHT = 900, 650
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    if flag == 1:
        intro_text = ["Вы проиграли.",
                      "Чтобы начать заново, нажмини пробел."
                      "Вы накопили : ", str(money)]
        fon = load_image('lose.png')
        screen.blit(fon, (100, 250))
    else:
        intro_text = ["Вы выиграли.",
                      "Чтобы начать заново, нажмини пробел."
                      "Вы накопили : ", str(money)]
        fon = load_image('win.png')
        screen.blit(fon, (100, 250))

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                play_game(money)
        pygame.display.flip()
        clock.tick(50)


def play_game(money):  # зацикливание игры
    WIDTH, HEIGHT = 900, 650
    fps = 60
    # параметры доски
    paddle_w = 200
    paddle_h = 25
    paddle_speed = 15
    paddle = pygame.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10, paddle_w, paddle_h)
    # параметры шарика
    ball_radius = 20
    ball_speed = 6
    ball_rect = int(ball_radius * 2 ** 0.5)
    ball = pygame.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect, ball_rect)
    dx, dy = 1, -1  # коэффициенты, отвечающие за направление даижения шарика и за смену направления при столкновении...
    # параметры блоков
    block_list = [pygame.Rect(10 + 110 * i, 10 + 60 * j, 100, 40) for i in range(8) for j in range(5)]
    color_list = [(0, 100, 0) for i in range(8) for j in range(5)]

    pygame.init()
    sc = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    def detect_collision(dx, dy, ball, rect):
        if dx > 0:  # если шарик сталкивается с блоком горизонтально.
            delta_x = ball.right - rect.left
        else:
            delta_x = rect.right - ball.left
        if dy > 0:  # если шарик сталкивается с блоком вертикально
            delta_y = ball.bottom - rect.top

        else:
            delta_y = rect.bottom - ball.top

        if abs(delta_x - delta_y) < 10:  # если шарик сталкивается с блоком под углом
            dx, dy = -dx, -dy
        elif delta_x > delta_y:
            dy = -dy
        elif delta_y > delta_x:
            dx = -dx
        return dx, dy

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        sc.fill('lightgreen')

        # рисование основных предметов
        [pygame.draw.rect(sc, color_list[color], block) for color, block in enumerate(block_list)]
        pygame.draw.rect(sc, pygame.Color('lightskyblue'), paddle)
        pygame.draw.circle(sc, pygame.Color('white'), ball.center, ball_radius)
        # движение шарика
        ball.x += ball_speed * dx
        ball.y += ball_speed * dy
        # отскок шарика справа слева
        if ball.centerx < ball_radius or ball.centerx > WIDTH - ball_radius:
            dx = -dx
        # отскок шарика сверху
        if ball.centery < ball_radius:
            dy = -dy
        # отскок от доски
        if ball.colliderect(paddle) and dy > 0:
            dx, dy = detect_collision(dx, dy, ball, paddle)
            money += 1
        # отскок послк удара о блок
        hit_index = ball.collidelist(block_list)
        if hit_index != -1:
            hit_rect = block_list.pop(hit_index)
            hit_color = color_list.pop(hit_index)
            dx, dy = detect_collision(dx, dy, ball, hit_rect)
            fps += 2  # увеличение скорости после каждого удара
            money += 1
        # вывод победа \ поражение игрока
        if ball.bottom > HEIGHT:
            end_screen(1, money)

        elif not len(block_list):
            end_screen(0, money)
        # движение доски
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and paddle.left > 0:
            paddle.left -= paddle_speed
        if key[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.right += paddle_speed

        pygame.display.flip()
        clock.tick(fps)


start_screen()
