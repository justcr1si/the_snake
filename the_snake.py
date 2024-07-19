from random import randrange, choice

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

# Скорость движения змейки
SPEED = 20

# Цвет текста
TEXT_COLOR = (0, 255, 0)

# Окно игры
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Описание игры
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Описание каждого объекта на поле."""

    def __init__(self, position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                 body_color=BOARD_BACKGROUND_COLOR):
        """Первично инициализирует объекты класса GameObject."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод, который рисует объект на игровом поле."""
        pass

    def draw_cell(self, position):
        """Рисует клетку на определенной позиции."""
        rect = pygame.Rect(position,
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def paint_over(self, position):
        """Закрашивает клетку на определенной позиции."""
        rect = pygame.Rect(position,
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class EatableObject(GameObject):
    """Описывает абстракцию еды на поле."""

    def __init__(self, body_color) -> None:
        """Инициализирует объект еды."""
        super().__init__(body_color=body_color)

    def generate_random_position(self):
        """Возвращает случайную позицию."""
        return (randrange(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE),
                randrange(0, GRID_HEIGHT * GRID_SIZE,
                          GRID_SIZE))

    def randomize_position(self, snake_positions):
        """Устанавливает объекту случайную позицию."""
        new_position = self.generate_random_position()
        while new_position in snake_positions:
            new_position = self.generate_random_position()
        self.position = new_position


class Apple(EatableObject):
    """
    Описывает абстракцию игрового яблока,
    который наследуется от GameObject.
    """

    def __init__(self, body_color=APPLE_COLOR) -> None:
        super().__init__(body_color)

    def draw(self):
        """Рисует клетку."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Описание абстракции змейки на игровом поле."""

    def __init__(self) -> None:
        """Присваивает экземпляру змейки все необходимые атрибуты."""
        super().__init__(body_color=SNAKE_COLOR)
        self.set_default_attributes()

    def set_default_attributes(self, direction=RIGHT):
        """Устанавливает начальные атрибуты змейке."""
        self.positions = [self.position]
        self.length = 1
        self.direction = direction
        self.last = None

    def update_direction(self, direction):
        """Обновляет направление движения змейки."""
        self.direction = direction

    def move(self):
        """Двигает змейку относительно направления движения."""
        position_x, position_y = self.get_head_position()
        step_x, step_y = self.direction
        new_head_position = ((position_x + (step_x * GRID_SIZE))
                             % SCREEN_WIDTH,
                             (position_y + (step_y * GRID_SIZE))
                             % SCREEN_HEIGHT)

        self.positions.insert(0, new_head_position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        self.draw_cell(self.get_head_position())

        if self.last:
            self.paint_over(self.last)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает всю змейку и ставит ей начальные координаты."""
        new_direction = choice([RIGHT, LEFT, UP, DOWN])
        self.set_default_attributes(direction=new_direction)


def handle_keys(game_object):
    """Обрабатывает входящие события по мере действия игры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)


def main():
    """Основная функция игры. Создаются экземпляры классов."""
    pygame.init()
    pygame.display.update()

    snake = Snake()
    apple = Apple()

    apple.randomize_position(snake.positions)
    apple.draw()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.move()
        snake.draw()
        snake_head = snake.get_head_position()

        if snake_head == apple.position:
            snake.length += 1
            snake.draw()
            apple.randomize_position(snake.positions)
            apple.draw()
        elif snake_head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()
