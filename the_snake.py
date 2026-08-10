from random import randint

import pygame as pg

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

DIRECTIONS = {
    # Если двиться ВЛЕВО или ВПРАВО, можно повернуть ВВЕРХ или ВНИЗ
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,

    # Если двигаться ВВЕРХ или ВНИЗ, можно повернуть ВЛЕВО или ВПРАВО
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}


# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Минимальная и максимальная скорость:
MIN_SPEED = 3
MAX_SPEED = 25
# Шаг скорости за одно нажатие
SPEED_STEP = 1

# Начальная скорость движения змейки:
speed = 3

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption(
    f'Игра "Змейка". Текущая скорость {speed} (Нажмите + или -)')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует базовые атрибуты игрового объекта."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки объекта(переопределяется в дочерних классах)."""
        raise NotImplementedError(
            f'Дочерний класс "{self.__class__.__name__}" '
            f'должен обязательно реализовать метод draw()!'
        )

    def draw_cell(self, position, color, border_color=None):
        """Отрисовывает одну ячейку."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color:
            pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Класс, представляющий яблоко на игровом поле."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Инициализирует яблоко и задает базовую позицию."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions or [])
        self.body_color = body_color

    def randomize_position(self, occupied_positions):
        """Генерирует случайные координаты вне тела змейки."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом экране."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color=body_color)
        self.reset()

    def draw(self):
        """Отрисовывает тело змейки на экране."""
        self.draw_cell(self.get_head_position(), self.body_color, BORDER_COLOR)

        if self.last:
            self.draw_cell(self.last,
                           BOARD_BACKGROUND_COLOR, BOARD_BACKGROUND_COLOR)

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

    def update_direction(self):
        """Обновляет текущее направление движения на следующее выбранное."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple):
        """Перемещает змейку.
        Проверяет столкновение с собственным телом и поедание яблока.
        """
        self.update_direction()

        direction_x, direction_y = self.direction
        head_x_coordinate, head_y_coordinate = self.get_head_position()
        self.position = (
            (head_x_coordinate + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y_coordinate + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        # Добавляем новую голову в начало списка
        self.positions.insert(0, self.position)

        # Проверяем, съела ли змейка яблоко
        if self.positions[0] == apple.position:
            self.length += 1
            apple.randomize_position(self.positions)
            self.last = None  # Хвост не удаляем, змейка растет
        else:
            # Если яблоко не съедено, удаляем лишний элемент с хвоста
            if len(self.positions) > self.length:
                self.last = self.positions.pop()
            else:
                self.last = None

# Функция обработки нажатия клавиш


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш клавиатуры для управления змейкой."""
    global speed

    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            return False
        if event.type == pg.KEYDOWN:
            current_state = (game_object.direction, event.key)
            game_object.next_direction = DIRECTIONS.get(
                current_state, game_object.direction)

            # Увеличение скорости (клавиши + или = )
            if event.key in (pg.K_EQUALS, pg.K_KP_PLUS):
                if speed < MAX_SPEED:
                    speed += SPEED_STEP
                    pg.display.set_caption(
                        f'Игра "Змейка". Текущая скорость {speed}'
                        f'(Нажмите + или -)'
                    )

            # Уменьшение скорости (клавиша - )
            elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                if speed > MIN_SPEED:
                    speed -= SPEED_STEP
                    pg.display.set_caption(
                        f'Игра "Змейка". Текущая скорость {speed}'
                        f'(Нажмите + или -)'
                    )
    return True


def main():
    """Главная функция запуска игры."""
    pg.init()
    snake = Snake(SNAKE_COLOR)
    apple = Apple(snake.positions, APPLE_COLOR)

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(speed)
        if not handle_keys(snake):
            break
        snake.move(apple)

        # Проверяем столкновение с телом ДО добавления новой головы
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
