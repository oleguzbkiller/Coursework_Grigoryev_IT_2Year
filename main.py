import random
import pygame

# Запуск и настройка Pygame
pygame.init()

# Основные параметры окна и частоты кадров
WIDTH = 800
HEIGHT = 600
FPS = 60

# Параметры физики птицы
GRAVITY = 0.3
JUMP_STRENGTH = -5

# Диапазон случайной ширины труб и расстояния между ними
PIPE_WIDTH_MIN = 50
PIPE_WIDTH_MAX = 200
PIPE_GAP_MIN = 120
PIPE_GAP_MAX = 250

PIPE_SPEED = 4
SPEED_INCREASE = 0.1
PIPE_INTERVAL = 1600

# Высота нижней зоны земли
GROUND_HEIGHT = 70

# Цвета объектов игры
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (70, 70, 70)

# Пороговые значения и названия достижений
ACHIEVEMENTS = {
    3: "Первые шаги",
    15: "Опытный пилот",
    30: "Эксперт",
    50: "Мастер"
}

# Создание игрового окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Таймер для ограничения количества кадров в секунду
clock = pygame.time.Clock()

# Шрифты для игрового интерфейса
font = pygame.font.Font(None, 48)
game_over_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 28)

# Начальные параметры птицы
bird_x = 150
bird_y = 300
bird_radius = 12
bird_velocity = 0

# Список всех труб на экране
pipes = []

# Время появления последней трубы
last_pipe_time = pygame.time.get_ticks()

# Состояние игры и текущий счёт
game_over = False
score = 0

# Список открытых достижений сохраняется между рестартами
unlocked_achievements = []


# Полностью возвращает игру в начальное состояние после проигрыша
def reset_game():
    global bird_y, bird_velocity, pipes, last_pipe_time, game_over, score

    bird_y = 300
    bird_velocity = 0
    pipes = []
    last_pipe_time = pygame.time.get_ticks()
    game_over = False
    score = 0


# Создаёт одну новую трубу со случайной шириной и размером прохода
def create_pipe():
    pipe_width = random.randint(PIPE_WIDTH_MIN, PIPE_WIDTH_MAX)
    pipe_gap = random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX)

    gap_y = random.randint(
        150,
        HEIGHT - GROUND_HEIGHT - 150
    )

    return {
        "x": WIDTH,
        "width": pipe_width,
        "gap_y": gap_y,
        "gap": pipe_gap,
        "passed": False
    }


# Рисует птицу и добавляет мягкое свечение вокруг неё
def draw_bird():
    glow = pygame.Surface((110, 110), pygame.SRCALPHA)
    center = (55, 55)

    # Несколько полупрозрачных кругов создают эффект градиентного свечения
    for radius, alpha in [
        (48, 12),
        (42, 20),
        (36, 32),
        (30, 50),
        (24, 75)
    ]:
        pygame.draw.circle(
            glow,
            (255, 255, 255, alpha),
            center,
            radius
        )

    # Накладываем слой свечения на основной экран
    screen.blit(
        glow,
        (bird_x - 55, int(bird_y) - 55)
    )

    # Рисуем саму птицу поверх свечения
    pygame.draw.circle(
        screen,
        WHITE,
        (bird_x, int(bird_y)),
        bird_radius
    )


# Проверяет столкновение птицы с границами экрана и трубами
def check_collision():
    bird_rect = pygame.Rect(
        bird_x - bird_radius,
        int(bird_y) - bird_radius,
        bird_radius * 2,
        bird_radius * 2
    )

    # Столкновение с верхней границей
    if bird_y - bird_radius <= 0:
        return True

    # Столкновение с землёй
    if bird_y + bird_radius >= HEIGHT - GROUND_HEIGHT:
        return True

    # Проверяем столкновение с каждой трубой
    for pipe in pipes:
        pipe_x = int(pipe["x"])
        pipe_width = pipe["width"]
        gap_y = pipe["gap_y"]
        pipe_gap = pipe["gap"]

        top_pipe_height = gap_y - pipe_gap // 2
        bottom_pipe_y = gap_y + pipe_gap // 2

        top_pipe_rect = pygame.Rect(
            pipe_x,
            0,
            pipe_width,
            top_pipe_height
        )

        bottom_pipe_rect = pygame.Rect(
            pipe_x,
            bottom_pipe_y,
            pipe_width,
            HEIGHT - GROUND_HEIGHT - bottom_pipe_y
        )

        if bird_rect.colliderect(top_pipe_rect):
            return True

        if bird_rect.colliderect(bottom_pipe_rect):
            return True

    return False


# Проверяет, достигнут ли новый порог достижений
def check_achievements():
    for threshold, name in ACHIEVEMENTS.items():
        if score >= threshold and name not in unlocked_achievements:
            unlocked_achievements.append(name)


# Основной игровой цикл
running = True

while running:
    # Обработка действий пользователя и системных событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Нажатие Space: прыжок или перезапуск после проигрыша
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                else:
                    bird_velocity = JUMP_STRENGTH

    # Обновление физики и объектов выполняется только во время игры
    if not game_over:
        # Гравитация постепенно увеличивает скорость падения
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        current_time = pygame.time.get_ticks()

        # Создаём новую трубу через заданный промежуток времени
        if current_time - last_pipe_time >= PIPE_INTERVAL:
            pipes.append(create_pipe())
            last_pipe_time = current_time

        # Увеличиваем скорость движения труб по мере роста счёта
        current_speed = PIPE_SPEED + score * SPEED_INCREASE

        # Двигаем трубы и проверяем, прошла ли птица очередную трубу
        for pipe in pipes:
            pipe["x"] -= current_speed

            if not pipe["passed"] and pipe["x"] + pipe["width"] < bird_x:
                pipe["passed"] = True
                score += 1
                check_achievements()

        # Удаляем трубы, которые полностью ушли за левый край экрана
        pipes = [
            pipe
            for pipe in pipes
            if pipe["x"] + pipe["width"] > 0
        ]

        # Если произошло столкновение, останавливаем игровую логику
        if check_collision():
            game_over = True

    # ---------- Отрисовка кадра ----------

    # Чёрный фон
    screen.fill(BLACK)

    # Отрисовка всех труб
    for pipe in pipes:
        pipe_x = int(pipe["x"])
        pipe_width = pipe["width"]
        gap_y = pipe["gap_y"]
        pipe_gap = pipe["gap"]

        top_pipe_height = gap_y - pipe_gap // 2
        bottom_pipe_y = gap_y + pipe_gap // 2

        pygame.draw.rect(
            screen,
            GRAY,
            (pipe_x, 0, pipe_width, top_pipe_height)
        )

        pygame.draw.rect(
            screen,
            GRAY,
            (
                pipe_x,
                bottom_pipe_y,
                pipe_width,
                HEIGHT - GROUND_HEIGHT - bottom_pipe_y
            )
        )

    # Отрисовка птицы
    draw_bird()

    # Серый прямоугольник земли
    pygame.draw.rect(
        screen,
        GRAY,
        (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    )

    # Отрисовка текущего счёта
    score_text = font.render(str(score), True, WHITE)
    screen.blit(
        score_text,
        (WIDTH // 2 - score_text.get_width() // 2, 30)
    )

    # Показываем количество открытых достижений
    achievement_text = small_font.render(
        f"Достижения: {len(unlocked_achievements)}/{len(ACHIEVEMENTS)}",
        True,
        WHITE
    )
    screen.blit(achievement_text, (20, 20))

    # Экран окончания игры
    if game_over:
        game_over_text = game_over_font.render(
            "GAME OVER",
            True,
            WHITE
        )

        restart_text = font.render(
            "Пробел - начать заново",
            True,
            WHITE
        )

        screen.blit(
            game_over_text,
            (
                WIDTH // 2 - game_over_text.get_width() // 2,
                HEIGHT // 2 - 100
            )
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT // 2 + 30
            )
        )

        # Выводим список открытых достижений после проигрыша
        if unlocked_achievements:
            achievement_text = small_font.render(
                "Разблокированы: " + ", ".join(unlocked_achievements),
                True,
                WHITE
            )

            screen.blit(
                achievement_text,
                (
                    WIDTH // 2 - achievement_text.get_width() // 2,
                    HEIGHT // 2 + 80
                )
            )

    # Показываем готовый кадр пользователю
    pygame.display.flip()

    # Ограничиваем частоту обновления игры значением FPS
    clock.tick(FPS)

# Корректно завершаем работу Pygame
pygame.quit()
