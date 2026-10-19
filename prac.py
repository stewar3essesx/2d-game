import pygame
import sys
import random
import math

# Инициализация
pygame.init()

# --- ВАШЕ НОВОЕ РАЗРЕШЕНИЕ ---
WIDTH, HEIGHT = 1620, 960

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический симулятор 2D: Законы Ньютона")
clock = pygame.time.Clock()

# Шрифты
try:
    font = pygame.font.SysFont("Consolas", 18)
    font_mid = pygame.font.SysFont("Consolas", 24, bold=True)
    font_big = pygame.font.SysFont("Consolas", 36, bold=True)
except:
    font = pygame.font.Font(None, 22)
    font_mid = pygame.font.Font(None, 28)
    font_big = pygame.font.Font(None, 40)

# --- РАЗМЕРЫ МИРА (Огромный космос) ---
WORLD_W, WORLD_H = 15000, 15000
START_X, START_Y = WORLD_W / 2, WORLD_H / 2


class Star:
    def __init__(self):
        self.x = random.randint(0, WORLD_W)
        self.y = random.randint(0, WORLD_H)
        self.size = random.randint(1, 3)
        self.depth = random.uniform(0.1, 1.0)

    def draw(self, surface, cam_x, cam_y):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        # Оптимизация: рисуем только то, что видно на экране
        if 0 <= screen_x <= WIDTH and 0 <= screen_y <= HEIGHT:
            color_val = int(100 + 155 * self.depth)
            pygame.draw.circle(surface, (color_val, color_val, color_val), (int(screen_x), int(screen_y)), self.size)


class Particle:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = 1.0
        self.decay = random.uniform(0.5, 2.0)
        self.size = random.randint(3, 8)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay * dt

    def draw(self, surface, cam_x, cam_y):
        if self.life > 0:
            screen_x = self.x - cam_x
            screen_y = self.y - cam_y
            alpha = int(self.life * 255)
            color = (255, int(150 * self.life), 0)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (int(screen_x) - self.size, int(screen_y) - self.size))


stars = [Star() for _ in range(2000)]
particles = []

# --- Переменные ракеты (в координатах МИРА) ---
x, y = START_X, START_Y
vx, vy = 0.0, 0.0
Fx, Fy = 0.0, 0.0
m = 10.0
t = 0.0
max_time = 60.0
MAX_FORCE = 500.0

final_x, final_y = 0, 0
final_vx, final_vy = 0, 0
final_ax, final_ay = 0, 0

running = True
while running:
    dt = clock.tick(60) / 1000.0
    dt *= 0.2

    # --- УПРАВЛЕНИЕ ---
    keys = pygame.key.get_pressed()

    if t < max_time:
        target_Fx = 0
        target_Fy = 0
        if keys[pygame.K_RIGHT]: target_Fx += MAX_FORCE
        if keys[pygame.K_LEFT]:  target_Fx -= MAX_FORCE
        if keys[pygame.K_DOWN]:  target_Fy += MAX_FORCE
        if keys[pygame.K_UP]:    target_Fy -= MAX_FORCE

        if Fx < target_Fx:
            Fx = min(target_Fx, Fx + 800 * dt)
        elif Fx > target_Fx:
            Fx = max(target_Fx, Fx - 800 * dt)

        if Fy < target_Fy:
            Fy = min(target_Fy, Fy + 800 * dt)
        elif Fy > target_Fy:
            Fy = max(target_Fy, Fy - 800 * dt)

        if keys[pygame.K_w]: m = min(1000.0, m + 0.1)
        if keys[pygame.K_s]: m = max(0.1, m - 0.1)
    else:
        Fx = 0
        Fy = 0

    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            t, vx, vy, Fx, Fy = 0.0, 0.0, 0.0, 0.0, 0.0
            x, y = START_X, START_Y
            m = 10.0
            particles.clear()

    # --- ФИЗИКА ---
    if t < max_time:
        ax = Fx / m
        ay = Fy / m
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt

        if t >= max_time:
            t = max_time
            final_x, final_y = x, y
            final_vx, final_vy = vx, vy
            final_ax, final_ay = ax, ay
            
    # --- СПАВН ЧАСТИЦ (Дым) ---
    if t < max_time:
        if abs(Fx) > 10:
            for _ in range(int(abs(Fx) / 20)):
                nozzle_x = x - math.copysign(15, Fx)
                particles.append(Particle(nozzle_x, y + random.randint(-5, 5), -Fx * 0.05, random.uniform(-15, 15)))

        if abs(Fy) > 10:
            for _ in range(int(abs(Fy) / 20)):
                nozzle_y = y - math.copysign(15, Fy)
                particles.append(Particle(x + random.randint(-5, 5), nozzle_y, random.uniform(-15, 15), -Fy * 0.05))

    for p in particles[:]:
        p.update(dt)
        if p.life <= 0: particles.remove(p)

    # --- КАМЕРА ---
    cam_x = x - WIDTH / 2
    cam_y = y - HEIGHT / 2

    # --- ОТРИСОВКА ---
    screen.fill((10, 10, 20))

    for star in stars:
        star.draw(screen, cam_x, cam_y)

    for p in particles:
        p.draw(screen, cam_x, cam_y)

    # Ракета
    if Fx != 0 or Fy != 0:
        angle = math.atan2(Fy, Fx)
    elif vx != 0 or vy != 0:
        angle = math.atan2(vy, vx)
    else:
        angle = 0

    dir_x = math.cos(angle)
    dir_y = math.sin(angle)
    perp_x = -dir_y
    perp_y = dir_x

    scr_x = x - cam_x
    scr_y = y - cam_y

    nose_x = scr_x + dir_x * 25
    nose_y = scr_y + dir_y * 25
    tail_x = scr_x - dir_x * 20
    tail_y = scr_y - dir_y * 20

    # Пламя
    if (abs(Fx) > 10 or abs(Fy) > 10) and t < max_time:
        flame_len = min(math.hypot(Fx, Fy) / 5, 50)
        p1 = (tail_x + perp_x * 8, tail_y + perp_y * 8)
        p2 = (tail_x - perp_x * 8, tail_y - perp_y * 8)
        p3 = (tail_x - dir_x * flame_len, tail_y - dir_y * flame_len)
        color = (255, 200, 0) if random.random() > 0.5 else (255, 100, 0)
        pygame.draw.polygon(screen, color, [p1, p2, p3])

    # Стабилизаторы
    stab1 = (scr_x - dir_x * 10 + perp_x * 15, scr_y - dir_y * 10 + perp_y * 15)
    stab2 = (scr_x - dir_x * 10 - perp_x * 15, scr_y - dir_y * 10 - perp_y * 15)
    stab3 = (scr_x - dir_x * 20, scr_y - dir_y * 20)
    pygame.draw.polygon(screen, (150, 150, 180), [stab1, stab2, stab3])

    # Корпус
    body_p1 = (nose_x, nose_y)
    body_p2 = (scr_x + perp_x * 10, scr_y + perp_y * 10)
    body_p3 = (scr_x - perp_x * 10, scr_y - perp_y * 10)
    pygame.draw.polygon(screen, (200, 200, 220), [body_p1, body_p2, body_p3])

    # Иллюминатор
    pygame.draw.circle(screen, (0, 150, 255), (int(scr_x + dir_x * 5), int(scr_y + dir_y * 5)), 5)

    # --- ИНТЕРФЕЙС (HUD) ---
    pygame.draw.rect(screen, (20, 20, 30), (10, 10, 320, 180))
    hud_texts = [
        f"Время: {t:.1f} / {max_time:.0f} с",
        f"Масса: {m:.1f} кг  [W/S]",
        f"Сила X: {Fx:.0f} Н | Y: {Fy:.0f} Н",
        f"Ускорение: X {Fx / m:.2f} | Y {Fy / m:.2f}",
        f"Скорость: X {vx:.1f} | Y {vy:.1f}",
    ]
    for i, txt in enumerate(hud_texts):
        screen.blit(font.render(txt, True, (200, 200, 200)), (20, 20 + i * 25))

    # --- МИНИ-КАРТА ---
    minimap_size = 200  # Сделал чуть больше для широкого экрана
    minimap_x = WIDTH - minimap_size - 20
    minimap_y = 20
    pygame.draw.rect(screen, (20, 20, 30), (minimap_x, minimap_y, minimap_size, minimap_size))
    pygame.draw.rect(screen, (100, 100, 100), (minimap_x, minimap_y, minimap_size, minimap_size), 2)

    map_x = minimap_x + (x / WORLD_W) * minimap_size
    map_y = minimap_y + (y / WORLD_H) * minimap_size
    pygame.draw.circle(screen, (0, 255, 255), (int(map_x), int(map_y)), 4)

    # Вектор скорости
    if abs(vx) > 1 or abs(vy) > 1:
        pygame.draw.line(screen, (0, 255, 100), (scr_x, scr_y), (scr_x + vx * 2, scr_y + vy * 2), 2)

    # --- ЭКРАН ОКОНЧАНИЯ ---
    if t >= max_time:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(WIDTH / 2 - 250, HEIGHT / 2 - 220, 500, 440)
        pygame.draw.rect(screen, (30, 30, 45), panel_rect)
        pygame.draw.rect(screen, (0, 255, 255), panel_rect, 3)

        title = font_big.render("СИМУЛЯЦИЯ ЗАВЕРШЕНА", True, (0, 255, 255))
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 2 - 190))

        sub = font.render(f"Время вышло: {max_time:.0f} секунд", True, (200, 200, 200))
        screen.blit(sub, (WIDTH / 2 - sub.get_width() / 2, HEIGHT / 2 - 140))

        dist = math.hypot(final_x - START_X, final_y - START_Y)
        speed = math.hypot(final_vx, final_vy)
        accel = math.hypot(final_ax, final_ay)

        stats = [
            f"Пройденный путь:   {dist:.1f} пикселей",
            f"Финальная скорость: {speed:.1f} м/с",
            f"Финальное ускорение: {accel:.1f} м/с²",
            f"Конечная масса:     {m:.1f} кг",
        ]

        for i, txt in enumerate(stats):
            stat_surf = font_mid.render(txt, True, (255, 255, 255))
            screen.blit(stat_surf, (WIDTH / 2 - stat_surf.get_width() / 2, HEIGHT / 2 - 80 + i * 45))

        restart = font_mid.render("Нажмите [R] для перезапуска", True, (255, 200, 0))
        screen.blit(restart, (WIDTH / 2 - restart.get_width() / 2, HEIGHT / 2 + 150))

    help_text = "Тяга: [←] [→] [↑] [↓] | Масса: [W] [S] | Сброс: [R]"
    screen.blit(font.render(help_text, True, (150, 150, 150)), (20, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()