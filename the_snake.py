from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 3

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовые атрибуты игрового объекта."""
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки объекта(переопределяется в дочерних классах)."""
        pass


class Apple(GameObject):
    """Класс, представляющий яблоко на игровом поле."""

    def __init__(self, position=None, body_color=APPLE_COLOR):
        """Инициализирует яблоко и задает базовую позицию."""
        super().__init__(position=position, body_color=body_color)
        self.position = position
        self.body_color = body_color

    def randomize_position(self, snake_positions):
        """Генерирует случайные координаты вне тела змейки."""
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            if snake_positions is None or self.position not in snake_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(
            self,
            body_color=SNAKE_COLOR,
            length=1,
            positions=None,
            direction=RIGHT,
            next_direction=None,
            last=None,
    ):
        start_position = positions[0] if positions is not None else None
        super().__init__(position=start_position, body_color=body_color)
        if positions is None:
            self.positions = [self.position]
        else:
            self.positions = positions

        self.body_color = body_color
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.last = last

    def draw(self):
        """Отрисовывает тело змейки на экране."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки к начальному"""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def move(self, apple):
        """Перемещает змейку.
        Проверяет столкновение с собственным телом и поедание яблока.
        """
        if self.next_direction:
            self.direction = self.next_direction
        new_head = self.get_head_position()
        x, y = new_head
        dx, dy = self.direction
        new_head = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        self.last = self.positions[-1]
        if self.positions[0] == apple.position:
            self.length += 1
            apple.randomize_position(self.positions)
        if self.positions[0] in self.positions[1:]:
            self.reset()
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Обновляет текущее направление движения на следующее выбранное."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


# Функция обработки нажатия клавиш
def handle_keys(game_object):
    """Обрабатывает нажатия клавиш клавиатуры для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Главная функция запуска игры."""
    pygame.init()
    snake = Snake(
        SNAKE_COLOR,
        1,
        [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)],
        (1, 0),
        (0, 1),
        None
    )
    apple = Apple((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), APPLE_COLOR)
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.move(apple)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
