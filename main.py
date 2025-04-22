import pgzrun
from pgzero.actor import Actor

WIDTH = 1440
HEIGHT = 847
TITLE = "Game"

# Меню игры
menu_items = ["Начать игру", "Вкл/Выкл музыку", "Выход"]
selected_item = 0
dead_selected_item = 0
death_sound_played = False
play_status = 'menu'  # 'menu', 'game', 'dead', 'victory'

# Фон с параллаксом
bg_images = []
bg_positions = [[0, 0] for _ in range(6)]
bg_speeds = [0.2, 0.3, 0.5, 0.7, 0.8, 1.0]
bg_colors = [(50, 50, 100), (70, 70, 150), (100, 100, 200),
             (50, 50, 100), (70, 70, 150), (100, 100, 200)]
use_images = False

# Звук
music_on = True
sounds_on = True
current_music = None

# Платформы
ground1 = Actor("ground1", anchor=("center", "top"))
ground1.pos = (WIDTH - 720, HEIGHT - 200)

platforms = [
    Actor("long_ground.png", anchor=("center", "top"), pos=(120, HEIGHT - 370)),
    Actor("long_ground.png", anchor=("center", "top"), pos=(760, HEIGHT - 550)),
    Actor("long_ground.png", anchor=("center", "top"), pos=(1550, HEIGHT - 370)),
]

# Позиции хп
hp_positions = [(20, 20), (70, 20), (120, 20)]
hp_images = []

# Победа
victory_timer = 0
victory_jump_timer = 0
last_enemy_death_complete = False

class Hero(Actor):
    def __init__(self):
        super().__init__("hero", anchor=("center", "bottom"))
        self.pos = (720, ground1.top)
        self.speed_x = 0
        self.speed_y = 0
        self.jump_power = -18
        self.gravity = 0.8
        self.on_ground = False
        self.health = 75
        self.hit_cooldown = 0
        self.facing_right = True

        # Анимации
        self.idle_images_right = ["hero_stands1.png", "hero_stands2.png", "hero_stands3.png", "hero_stands4.png"]
        self.idle_images_left = ["hero_stands5.png", "hero_stands6.png", "hero_stands7.png", "hero_stands8.png"]

        self.run_images_right = ["hero_run1.png", "hero_run2.png", "hero_run3.png", "hero_run4.png",
                                 "hero_run5.png", "hero_run6.png", "hero_run7.png", "hero_run8.png"]
        self.run_images_left = ["hero_run9.png", "hero_run10.png", "hero_run11.png", "hero_run12.png",
                                "hero_run13.png", "hero_run14.png", "hero_run15.png", "hero_run16.png"]

        self.jump_images_right = ["hero_jump4.png", "hero_jump5.png", "hero_jump6.png", "hero_jump7.png", "hero_jump8.png"]
        self.jump_images_left = ["hero_jump12.png", "hero_jump13.png", "hero_jump14.png", "hero_jump15.png", "hero_jump16.png"]

        self.hit_images_right = ["hero_hit1.png", "hero_hit2.png", "hero_hit3.png", "hero_hit4.png",
                                 "hero_hit5.png", "hero_hit6.png", "hero_hit7.png"]
        self.hit_images_left = ["hero_hit8.png", "hero_hit9.png", "hero_hit10.png", "hero_hit11.png",
                                "hero_hit12.png", "hero_hit13.png", "hero_hit14.png"]

        self.is_jumping = False
        self.is_hitting = False

        self.idle_index = 0
        self.run_index = 0
        self.jump_index = 0
        self.hit_index = 0

        self.idle_timer = 0
        self.run_timer = 0
        self.jump_timer = 0
        self.hit_timer = 0

        self.IDLE_DELAY = 0.3
        self.RUN_DELAY = 0.1
        self.JUMP_DELAY = 0.1
        self.HIT_DELAY = 0.05

    def reset(self):
        self.pos = (720, ground1.top)
        self.speed_x = 0
        self.speed_y = 0
        self.health = 75
        self.hit_cooldown = 0
        self.on_ground = False
        self.is_jumping = False
        self.is_hitting = False
        self.facing_right = True

    def move(self):
        if keyboard.A and keyboard.D:
            self.speed_x = 0
        elif keyboard.A:
            self.speed_x = -8
        elif keyboard.D:
            self.speed_x = 8
        else:
            self.speed_x = 0

    def jump(self):
        if self.on_ground:
            self.speed_y = self.jump_power
            self.on_ground = False

    def hit(self):
        if not self.is_hitting and self.hit_cooldown <= 0:
            self.is_hitting = True
            self.hit_index = 0
            self.hit_timer = 0
            self.image = self.hit_images_right[0] if self.facing_right else self.hit_images_left[0]
            play_sound('hit.wav')

    def take_hit(self, damage):
        if self.hit_cooldown <= 0:
            self.health -= damage
            self.hit_cooldown = 1.0
            play_sound('hero_hit.wav')
            return True
        return False

    def animate(self, dt):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt

        if self.is_hitting:
            self.hit_timer += dt
            if self.hit_timer >= self.HIT_DELAY:
                self.hit_timer = 0
                self.hit_index += 1
                if self.hit_index >= len(self.hit_images_right):
                    self.is_hitting = False
                    self.hit_index = 0
                    self.hit_cooldown = 0.1
                else:
                    self.image = self.hit_images_right[self.hit_index] if self.facing_right else self.hit_images_left[self.hit_index]
            return

        if not self.on_ground:
            self.jump_timer += dt
            if self.jump_timer >= self.JUMP_DELAY:
                self.jump_timer = 0
                self.jump_index = (self.jump_index + 1) % len(self.jump_images_right)
                self.image = self.jump_images_right[self.jump_index] if self.facing_right else self.jump_images_left[self.jump_index]
            return

        if self.speed_x != 0:
            self.run_timer += dt
            if self.run_timer >= self.RUN_DELAY:
                self.run_timer = 0
                self.run_index = (self.run_index + 1) % len(self.run_images_right)
                self.image = self.run_images_right[self.run_index] if self.facing_right else self.run_images_left[self.run_index]
        else:
            self.idle_timer += dt
            if self.idle_timer >= self.IDLE_DELAY:
                self.idle_timer = 0
                self.idle_index = (self.idle_index + 1) % len(self.idle_images_right)
                self.image = self.idle_images_right[self.idle_index] if self.facing_right else self.idle_images_left[self.idle_index]


# Создание героя
hero = Hero()

# Анимации врагов
enemies_idle_lst_right = ["enemy_idle1.png", "enemy_idle2.png", "enemy_idle3.png", "enemy_idle4.png"]
enemies_idle_lst_left = ["enemy_idle5.png", "enemy_idle6.png", "enemy_idle7.png", "enemy_idle8.png"]

enemies_walk_lst_right = ["enemy_walk1.png", "enemy_walk2.png", "enemy_walk3.png", "enemy_walk4.png",
                          "enemy_walk5.png", "enemy_walk6.png", "enemy_walk7.png", "enemy_walk8.png", "enemy_walk9.png"]
enemies_walk_lst_left = ["enemy_walk10.png", "enemy_walk11.png", "enemy_walk12.png", "enemy_walk13.png",
                         "enemy_walk14.png", "enemy_walk15.png", "enemy_walk16.png", "enemy_walk17.png",
                         "enemy_walk18.png"]

enemies_dead_lst_right = ["enemy_dead1.png", "enemy_dead2.png", "enemy_dead3.png", "enemy_dead4.png", "enemy_dead5.png",
                          "enemy_dead6.png"]
enemies_dead_lst_left = ["enemy_dead7.png", "enemy_dead8.png", "enemy_dead9.png", "enemy_dead10.png",
                         "enemy_dead11.png", "enemy_dead12.png"]

enemies_hit_lst_right = ["enemy_hit1.png", "enemy_hit2.png", "enemy_hit3.png", "enemy_hit4.png", "enemy_hit5.png"]
enemies_hit_lst_left = ["enemy_hit6.png", "enemy_hit7.png", "enemy_hit8.png", "enemy_hit9.png", "enemy_hit10.png"]

class Enemy:
    def __init__(self, platform_index, patrol_range=200):
        self.platform = platforms[platform_index]
        self.patrol_range = patrol_range
        self.x = self.platform.x - patrol_range // 2
        self.y = self.platform.top - 36
        self.speed = 2
        self.direction = 1  # 1 - вправо, -1 - влево (для движения)
        self.facing_right = True  # Текущая ориентация спрайта
        self.state = "walk"
        self.state_timer = 0
        self.idle_time = 3
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_delay = 0.1
        self.width = 60
        self.height = 80
        self.health = 75
        self.alive = True
        self.hit_cooldown = 0
        self.death_animation_timer = 0
        self.death_animation_delay = 0.1
        self.death_animation_index = 0
        self.death_animation_complete = False
        self.death_timer = 0
        self.death_duration = 1.5
        self.attack_cooldown = 0
        self.attack_range = 150  # Дистанция атаки
        self.attack_damage = 25  # Урон от атаки
        self.attack_state = False  # Состояние атаки
        self.attack_animation_index = 0
        self.attack_animation_timer = 0
        self.attack_animation_delay = 0.3
        self.attack_hitbox_x = 80  # Горизонтальное расстояние атаки
        self.attack_hitbox_y = 100  # Вертикальное расстояние атаки
        self.has_hit = False  # Флаг, что удар уже нанесен в этой анимации
        self.is_last_enemy = False  # Флаг, что это последний враг

    def update(self, dt):
        if not self.alive:
            self.death_animation_timer += dt
            if not self.death_animation_complete:
                if self.death_animation_timer >= self.death_animation_delay:
                    self.death_animation_timer = 0
                    self.death_animation_index += 1
                    if self.death_animation_index >= len(enemies_dead_lst_right):
                        self.death_animation_complete = True
                        self.death_animation_index = len(enemies_dead_lst_right) - 1
                        if self.is_last_enemy:
                            global last_enemy_death_complete
                            last_enemy_death_complete = True
            else:
                self.death_timer += dt
            return

        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Проверка расстояния до героя с учетом вертикали
        hero_distance_x = abs(hero.x - self.x)
        hero_distance_y = abs(hero.y - self.y)

        # Проверяем, находится ли враг и герой на одной платформе (примерно на одной высоте)
        same_platform = hero_distance_y < 100

        if same_platform and hero_distance_x < self.attack_range and self.attack_cooldown <= 0:
            # Поворачиваемся к герою
            self.facing_right = hero.x > self.x
            self.attack_state = True
            self.attack_animation_index = 0
            self.attack_animation_timer = 0
            self.attack_cooldown = 2.0
            self.state = "idle"
            self.has_hit = False

        if self.attack_state:
            self.attack_animation_timer += dt
            if self.attack_animation_timer >= self.attack_animation_delay:
                self.attack_animation_timer = 0
                self.attack_animation_index += 1

                # Наносим урон только в определенных кадрах анимации
                if 2 <= self.attack_animation_index <= 3 and not self.has_hit:
                    # Проверяем расстояние до героя по X и Y
                    hero_distance_x = abs(hero.x - self.x)
                    hero_distance_y = abs(hero.y - self.y)

                    if (hero_distance_x < self.attack_hitbox_x and
                            hero_distance_y < self.attack_hitbox_y and
                            hero.hit_cooldown <= 0):

                        if hero.take_hit(self.attack_damage):
                            play_sound('hero_hit.wav')

                        self.has_hit = True

                if self.attack_animation_index >= len(enemies_hit_lst_right):
                    self.attack_state = False
                    self.attack_animation_index = 0
                    self.has_hit = False
            return

        if self.state == "idle":
            self.state_timer += dt
            if self.state_timer >= self.idle_time:
                self.state = "walk"
                self.state_timer = 0
                self.direction *= -1
                self.facing_right = self.direction == 1
        elif self.state == "walk":
            self.x += self.speed * self.direction

            left_bound = self.platform.x - self.patrol_range // 2 + self.width // 2
            right_bound = self.platform.x + self.patrol_range // 2 - self.width // 2

            if (self.direction == -1 and self.x <= left_bound) or \
                    (self.direction == 1 and self.x >= right_bound):
                self.state = "idle"
                self.state_timer = 0
                self.facing_right = self.direction == 1
                self.x = left_bound if self.direction == -1 else right_bound

        self.animation_timer += dt
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            if self.state == "idle":
                self.animation_index = (self.animation_index + 1) % len(enemies_idle_lst_right)
            elif self.state == "walk":
                self.animation_index = (self.animation_index + 1) % len(enemies_walk_lst_right)

    def take_hit(self):
        if self.hit_cooldown <= 0 and self.alive:
            self.health -= 25
            self.hit_cooldown = 0.5
            if self.health <= 0:
                self.alive = False
                self.death_animation_index = 0
                self.death_animation_timer = 0
                self.death_animation_complete = False
                self.death_timer = 0

                # Проверяем, является ли этот враг последним
                alive_enemies = [e for e in enemies if e.alive]
                if len(alive_enemies) == 0:
                    self.is_last_enemy = True

                play_sound('enemy_death.wav')
            return True
        return False

    def draw(self):
        if not self.alive:
            if self.death_timer < self.death_duration or (self.is_last_enemy and not last_enemy_death_complete):
                try:
                    if self.facing_right:
                        image = enemies_dead_lst_right[min(self.death_animation_index, len(enemies_dead_lst_right) - 1)]
                    else:
                        image = enemies_dead_lst_left[min(self.death_animation_index, len(enemies_dead_lst_left) - 1)]
                    screen.blit(image, (self.x - self.width // 2, self.y - self.height))
                except:
                    screen.draw.rect(Rect(self.x - self.width // 2, self.y - self.height,
                                      self.width, self.height), "darkred")
            return

        try:
            if self.attack_state:
                if self.facing_right:
                    image = enemies_hit_lst_right[self.attack_animation_index % len(enemies_hit_lst_right)]
                else:
                    image = enemies_hit_lst_left[self.attack_animation_index % len(enemies_hit_lst_left)]
            elif self.state == "idle":
                if self.facing_right:
                    image = enemies_idle_lst_right[self.animation_index % len(enemies_idle_lst_right)]
                else:
                    image = enemies_idle_lst_left[self.animation_index % len(enemies_idle_lst_left)]
            else:
                if self.direction == 1:
                    image = enemies_walk_lst_right[self.animation_index % len(enemies_walk_lst_right)]
                else:
                    image = enemies_walk_lst_left[self.animation_index % len(enemies_walk_lst_left)]

            screen.blit(image, (self.x - self.width // 2, self.y - self.height))

            health_width = 60
            health_height = 6
            health_x = self.x - health_width // 2
            health_y = self.y - self.height - 12

            screen.draw.filled_rect(
                Rect(health_x, health_y, health_width, health_height),
                (50, 50, 50)
            )
            screen.draw.filled_rect(
                Rect(health_x, health_y, health_width * (self.health / 75), health_height),
                (200, 30, 30)
            )
        except:
            screen.draw.rect(Rect(self.x - self.width // 2, self.y - self.height, self.width, self.height), "red")

# Функция создания врагов
def create_enemies():
    return [
        Enemy(0, patrol_range=150),
        Enemy(1, patrol_range=430)
    ]

# Список врагов
enemies = create_enemies()

# Загрузка ресурсов
def load_resources():
    global use_images, current_music, hp_images
    try:
        bg1 = Actor("background6", anchor=("left", "top"))
        bg2 = Actor("background5", anchor=("left", "top"))
        bg3 = Actor("background4", anchor=("left", "top"))
        bg4 = Actor("background3", anchor=("left", "top"))
        bg5 = Actor("background2", anchor=("left", "top"))
        bg6 = Actor("background1", anchor=("left", "top"))

        bg_images.extend([bg6, bg5, bg4, bg3, bg2, bg1])
        use_images = True

        # Загрузка здоровья
        for i in range(3):
            hp = Actor("hp.png", anchor=("left", "top"))
            hp.pos = hp_positions[i]
            hp_images.append(hp)
    except:
        use_images = False

    try:
        current_music = 'theme1.mp3'
        if music_on:
            music.play(current_music)
    except:
        pass

load_resources()

def update(dt):
    global victory_timer, victory_jump_timer

    for i in range(len(bg_speeds)):
        bg_positions[i][0] -= bg_speeds[i]
        if bg_positions[i][0] <= -WIDTH:
            bg_positions[i][0] = 0

    if play_status == 'game':
        update_game(dt)

    elif play_status == 'victory':
        victory_timer += dt
        victory_jump_timer += dt

        if victory_jump_timer >= 1:
            victory_jump_timer = 0
            hero.speed_y = hero.jump_power * 0.7

        hero.speed_y += hero.gravity
        hero.y += hero.speed_y

        if hero.colliderect(ground1) and hero.speed_y > 0:
            hero.bottom = ground1.top
            hero.speed_y = 0


def update_game(dt):
    global play_status, death_sound_played, last_enemy_death_complete

    for enemy in enemies[:]:
        enemy.update(dt)

        if hero.is_hitting:
            if hero.colliderect(Rect(enemy.x - enemy.width // 2, enemy.y - enemy.height, enemy.width, enemy.height)):
                if enemy.take_hit():
                    hero.speed_x = 5 if hero.facing_right else -5
                    hero.speed_y = -5

    enemies[:] = [e for e in enemies if e.alive or e.death_timer < e.death_duration or (e.is_last_enemy and not last_enemy_death_complete)]

    alive_enemies = [e for e in enemies if e.alive]
    if len(alive_enemies) == 0 and play_status == 'game':
        if last_enemy_death_complete or all(e.death_animation_complete for e in enemies if not e.alive):
            play_status = 'victory'
            play_sound('victory.wav')

    hero.move()

    if hero.speed_x < 0:
        hero.facing_right = False
    elif hero.speed_x > 0:
        hero.facing_right = True

    prev = (hero.left, hero.right, hero.top, hero.bottom)

    hero.speed_y += hero.gravity
    hero.y += hero.speed_y
    hero.x += hero.speed_x
    hero.on_ground = False

    if hero.colliderect(ground1):
        collide_with_platform(hero, ground1, prev)

    for platform in platforms:
        if hero.colliderect(platform):
            collide_with_platform(hero, platform, prev)

    hero.x = max(hero.width // 2, min(WIDTH - hero.width // 2, hero.x))

    if hero.top > HEIGHT or hero.health <= 0:
        play_status = 'dead'
        death_sound_played = False

    hero.animate(dt)


def collide_with_platform(actor, platform, prev):
    prev_left, prev_right, prev_top, prev_bottom = prev

    if actor.speed_y > 0 and prev_bottom <= platform.top:
        actor.bottom = platform.top
        actor.speed_y = 0
        actor.on_ground = True
    elif actor.speed_y < 0 and prev_top >= platform.bottom:
        actor.top = platform.bottom
        actor.speed_y = 0

    if prev_right <= platform.left and actor.right > platform.left:
        actor.right = platform.left
        actor.speed_x = 0
    elif prev_left >= platform.right and actor.left < platform.right:
        actor.left = platform.right
        actor.speed_x = 0


def draw_parallax_background():
    if use_images:
        for i, bg in enumerate(bg_images):
            bg.pos = (bg_positions[i][0], 0)
            bg.draw()
            bg.pos = (bg_positions[i][0] + WIDTH, 0)
            bg.draw()
    else:
        for i in range(len(bg_colors)):
            screen.draw.filled_rect(Rect(bg_positions[i][0], 0, WIDTH, HEIGHT), bg_colors[i])
            screen.draw.filled_rect(Rect(bg_positions[i][0] + WIDTH, 0, WIDTH, HEIGHT), bg_colors[i])


def draw_game():
    draw_parallax_background()
    ground1.draw()
    for platform in platforms:
        platform.draw()
    for enemy in enemies:
        enemy.draw()
    hero.draw()

    full_hearts = hero.health // 25
    for i in range(3):
        if i < full_hearts:
            hp_images[i].image = "hp.png"
            hp_images[i].draw()


def draw_menu():
    draw_parallax_background()

    screen.draw.text("by ZHUROV", bottomleft=(20, 830), color="grey", fontsize=30, fontname='pixel')
    menu_background = Actor("back_menu")
    menu_background.center = (723, 423)
    menu_background.draw()
    screen.draw.text("МЕНЮ", center=(720, 240), color="white", fontsize=43, fontname='pixel')

    for i, item in enumerate(menu_items):
        color = (99, 194, 197) if i == selected_item else "white"
        y_pos = 350 + i * 70
        screen.draw.text(item, center=(725, y_pos), color=color, fontsize=36, fontname='pixel')

        if i == 1:
            sound_status = "sound_on.jpg" if music_on else "sound_off.jpg"
            sound_img = Actor(f"{sound_status}", anchor=("left", "top"))
            sound_img.draw()
def draw_victory_screen():
    screen.draw.text("ПОБЕДА", center=(WIDTH // 2, HEIGHT // 2 - 50),
                     color=(0, 255, 0), fontsize=100, fontname='pixel')

    screen.draw.text("чтобы выйти нажми ESC", center=(WIDTH // 2, HEIGHT // 2 + 50),
                     color="white", fontsize=40, fontname='pixel')


def draw_dead_screen():
    global death_sound_played
    music.fadeout(2)

    if not death_sound_played:
        try:
            play_sound('laughter.mp3')
            death_sound_played = True
        except:
            pass

    bg_dead = Actor("back_dead.png", anchor=("left", "top"))
    bg_dead.draw()

    screen.draw.text("МЕРТВ", center=(WIDTH // 2, HEIGHT // 2 - 100),
                     color="red", fontsize=100, fontname='pixel')

    color = (99, 194, 197) if dead_selected_item == 0 else "white"
    screen.draw.text("Начать заново", center=(WIDTH // 2, HEIGHT // 2 + 50),
                     color=color, fontsize=50, fontname='pixel')

    color = (99, 194, 197) if dead_selected_item == 1 else "white"
    screen.draw.text("В меню", center=(WIDTH // 2, HEIGHT // 2 + 120),
                     color=color, fontsize=50, fontname='pixel')


def play_sound(sound_name):
    if not sounds_on:
        return
    try:
        getattr(sounds, sound_name).play()
    except:
        pass


def on_key_down(key):
    global selected_item, dead_selected_item
    global play_status, music_on, sounds_on
    global enemies, last_enemy_death_complete, death_sound_played

    if play_status == 'menu':
        if key in (keys.DOWN, keys.S):
            selected_item = (selected_item + 1) % len(menu_items)
            play_sound('select.mp3')
        elif key in (keys.UP, keys.W):
            selected_item = (selected_item - 1) % len(menu_items)
            play_sound('select.mp3')
        elif key == keys.RETURN:
            play_sound('confirm.mp3')
            if selected_item == 0:
                hero.reset()
                enemies = create_enemies()
                last_enemy_death_complete = False
                play_status = 'game'
            elif selected_item == 1:
                music_on = not music_on
                sounds_on = not sounds_on
                if music_on and current_music:
                    music.play(current_music)
                else:
                    music.stop()
            elif selected_item == 2:
                exit()

    elif play_status == 'game':
        if key in (keys.W, keys.UP):
            hero.jump()
        elif key == keys.SPACE:
            hero.hit()

    elif play_status == 'dead':
        if key in (keys.DOWN, keys.S):
            dead_selected_item = (dead_selected_item + 1) % 2
            play_sound('select.mp3')
        elif key in (keys.UP, keys.W):
            dead_selected_item = (dead_selected_item - 1) % 2
            play_sound('select.mp3')
        elif key == keys.RETURN:
            play_sound('confirm.mp3')
            if dead_selected_item == 0:
                hero.reset()
                enemies = create_enemies()
                last_enemy_death_complete = False
                play_status = 'game'
                music.play(current_music)
                death_sound_played = False
            else:
                play_status = 'menu'
                music.play(current_music)
                death_sound_played = False


def on_key_up(key):
    global play_status
    if play_status in ['game', 'victory'] and key == keys.ESCAPE:
        play_status = 'menu'
        play_sound('back.mp3')


def draw():
    screen.clear()

    if play_status == 'menu':
        draw_menu()
    elif play_status == 'game':
        draw_game()
    elif play_status == 'dead':
        draw_game()
        draw_dead_screen()
    elif play_status == 'victory':
        draw_game()
        draw_victory_screen()


if music_on and current_music:
    music.play(current_music)

pgzrun.go()