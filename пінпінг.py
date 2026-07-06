from pygame import *
import socket
import json
from threading import Thread

WIDTH, HEIGHT = 800, 600
init()
mixer.init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

game_mode = "menu"
player_name = "Гравець 1"
selected_ball_color = (255, 255, 255)
purchased_skins = ["Білий"]
score_points = 0

font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
font_small = font.Font(None, 28)

try:
    img_back = transform.scale(image.load("background.png"), (WIDTH, HEIGHT))
    img_ball = transform.scale(image.load("ball.png"), (20, 20))
    img_pad1 = transform.scale(image.load("paddle1.png"), (20, 100))
    img_pad2 = transform.scale(image.load("paddle2.png"), (20, 100))
    textures_loaded = True
except:
    textures_loaded = False

try:
    snd_wall = mixer.Sound("wall.wav")
    snd_paddle = mixer.Sound("paddle.wav")
    sounds_loaded = True
except:
    sounds_loaded = False


def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over, score_points
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
                    if sounds_loaded and 'sound_event' in game_state:
                        if game_state['sound_event'] == 'wall_hit':
                            snd_wall.play()
                        elif game_state['sound_event'] == 'platform_hit':
                            snd_paddle.play()
        except:
            game_state["winner"] = -1
            break


def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse_pos = mouse.get_pos()
    click = mouse.get_pressed()

    if x + w > mouse_pos[0] > x and y + h > mouse_pos[1] > y:
        draw.rect(screen, active_color, (x, y, w, h), border_radius=10)
        if click[0] == 1 and action is not None:
            time.delay(200)
            action()
    else:
        draw.rect(screen, inactive_color, (x, y, w, h), border_radius=10)

    text_surf = font_main.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surf, text_rect)


def start_game():
    global game_mode, my_id, game_state, buffer, client, game_over
    game_over = False
    my_id, game_state, buffer, client = connect_to_server()
    Thread(target=receive, daemon=True).start()
    game_mode = "game"


def open_settings(): global game_mode; game_mode = "settings"


def open_shop(): global game_mode; game_mode = "shop"


def open_menu(): global game_mode; game_mode = "menu"


def quit_game(): exit()


def render_menu():
    screen.fill((40, 40, 40))
    title = font_win.render("ПІНГ-ПОНГ LOBBY", True, (0, 255, 200))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    draw_button("Грати", WIDTH // 2 - 100, 220, 200, 50, (0, 150, 0), (0, 200, 0), start_game)
    draw_button("Налаштування", WIDTH // 2 - 100, 290, 200, 50, (150, 150, 0), (200, 200, 0), open_settings)
    draw_button("Магазин скінів", WIDTH // 2 - 100, 360, 200, 50, (0, 100, 150), (0, 150, 200), open_shop)
    draw_button("Вихід", WIDTH // 2 - 100, 430, 200, 50, (150, 0, 0), (200, 0, 0), quit_game)


def render_settings():
    global player_name
    screen.fill((30, 50, 60))
    title = font_main.render("Налаштування гравця", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    info_text = font_main.render(f"Нікнейм: {player_name}", True, (255, 255, 0))
    screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 220))

    tip_text = font_small.render("(Натискайте клавіші на клавіатурі, щоб змінити ім'я)", True, (200, 200, 200))
    screen.blit(tip_text, (WIDTH // 2 - tip_text.get_width() // 2, 270))

    draw_button("Назад в меню", WIDTH // 2 - 100, 450, 200, 50, (100, 100, 100), (150, 150, 150), open_menu)


def render_shop():
    global selected_ball_color, score_points
    screen.fill((50, 30, 50))

    title = font_main.render(f"Магазин скінів (Бали: {score_points})", True, (255, 215, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    def buy_gold():
        global score_points, selected_ball_color
        if "Золотий" not in purchased_skins and score_points >= 10:
            score_points -= 10
            purchased_skins.append("Золотий")
        if "Золотий" in purchased_skins: selected_ball_color = (255, 215, 0)

    def buy_neon():
        global score_points, selected_ball_color
        if "Неон" not in purchased_skins and score_points >= 20:
            score_points -= 20
            purchased_skins.append("Неон")
        if "Неон" in purchased_skins: selected_ball_color = (0, 255, 255)

    def select_white():
        global selected_ball_color; selected_ball_color = (255, 255, 255)

    draw_button("Стандарт (Білий) - Безкоштовно", 150, 150, 500, 50, (80, 80, 80), (120, 120, 120), select_white)

    txt_gold = "Обрати Золотий" if "Золотий" in purchased_skins else "Купити Золотий (10 балів)"
    draw_button(txt_gold, 150, 230, 500, 50, (150, 120, 0), (200, 170, 0), buy_gold)

    txt_neon = "Обрати Неоновий" if "Неон" in purchased_skins else "Купити Неоновий (20 балів)"
    draw_button(txt_neon, 150, 310, 500, 50, (0, 120, 150), (0, 170, 200), buy_neon)

    draw_button("Назад в меню", WIDTH // 2 - 100, 450, 200, 50, (100, 100, 100), (150, 150, 150), open_menu)


game_over = False
winner = None
you_winner = None

while True:
    events = event.get()
    for e in events:
        if e.type == QUIT:
            exit()

        if game_mode == "settings" and e.type == KEYDOWN:
            if e.key == K_BACKSPACE:
                player_name = player_name[:-1]
            elif len(player_name) < 15 and e.unicode.isalnum():
                player_name += e.unicode

    if game_mode == "menu":
        render_menu()
    elif game_mode == "settings":
        render_settings()
    elif game_mode == "shop":
        render_shop()

    elif game_mode == "game":
        if "countdown" in game_state and game_state["countdown"] > 0:
            screen.fill((0, 0, 0))
            countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
            screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
            display.update()
            continue

        if "winner" in game_state and game_state["winner"] is not None:
            screen.fill((20, 20, 20))

            if you_winner is None:
                if game_state["winner"] == my_id:
                    you_winner = True
                    score_points += 5
                else:
                    you_winner = False

            text = f"Перемога, {player_name}!" if you_winner else "Пощастить наступним разом!"
            win_text = font_win.render(text, True, (255, 215, 0))
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_text, text_rect)

            draw_button("В головне меню", WIDTH // 2 - 120, HEIGHT // 2 + 100, 240, 50, (100, 100, 100),
                        (150, 150, 150), open_menu)

            display.update()
            continue

        if game_state:
            if textures_loaded:
                screen.blit(img_back, (0, 0))
            else:
                screen.fill((30, 30, 30))

            if textures_loaded:
                screen.blit(img_pad1, (20, game_state['paddles']['0']))
                screen.blit(img_pad2, (WIDTH - 40, game_state['paddles']['1']))
            else:
                draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
                draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))

            if textures_loaded and selected_ball_color == (255, 255, 255):
                screen.blit(img_ball, (game_state['ball']['x'] - 10, game_state['ball']['y'] - 10))
            else:
                draw.circle(screen, selected_ball_color, (game_state['ball']['x'], game_state['ball']['y']), 10)

            score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True,
                                          (255, 255, 255))
            screen.blit(score_text, (WIDTH // 2 - 25, 20))

            name_tag = font_small.render(f"Гравець: {player_name}", True, (200, 200, 200))
            screen.blit(name_tag, (20, 20))

        else:
            screen.fill((0, 0, 0))
            waiting_text = font_main.render("Очікування гравців...", True, (255, 255, 255))
            screen.blit(waiting_text, (WIDTH // 2 - waiting_text.get_width() // 2, HEIGHT // 2))

        keys = key.get_pressed()
        if keys[K_w]:
            client.send(b"UP")
        elif keys[K_s]:
            client.send(b"DOWN")

    display.update()
    clock.tick(60)