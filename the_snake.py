import pygame
import pygame.freetype
from random import randrange, choice
from typing import Optional

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

# Цвет отравленной еды
POISONED_FOOD_COLOR = (100, 40, 0)

# Цвет камня
STONE_COLOR = (235, 245, 255)

# Скорость движения змейки
SPEED = 10

# Цвет текста
TEXT_COLOR = (0, 255, 0)

# Окно игры
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Описание игры
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()

# Создание списка позиций объектов.
positions = []


class GameObject:
    """Описание каждого объекта на поле."""

    def __init__(self) -> None:
        """Первично инициализирует объекты класса GameObject."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: Optional[tuple[int, int, int]] = None

    def draw(self):
        """Рисует объект на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Возвращает случайную позицию."""
        position = (
            randrange(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE),
            randrange(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE),
        )
        return position

    def update_position(self):
        """Обновляет позицию объекта."""
        self.position = self.randomize_position()


class Food(GameObject):
    """Описывает абстракцию еды на поле."""

    def __init__(self) -> None:
        """Инициализирует объект еды."""
        self.position = self.randomize_position()
        positions.append(self.position)
        self.body_color = None


class PoisonedFood(Food, GameObject):
    """Описывает ядовитую еду."""

    def __init__(self) -> None:
        """Инициализирует объект ядовитой еды."""
        super().__init__()
        self.body_color = POISONED_FOOD_COLOR


class Apple(Food, GameObject):
    """
    Описывает абстракцию игрового яблока,
    который наследуется от GameObject.
    """

    def __init__(self) -> None:
        """Инициализирует объект яблока и присваивает ему цвет и позицию."""
        super().__init__()
        self.body_color = APPLE_COLOR


class Stone(GameObject):
    """Описывает абстракцию игрового камня."""

    def __init__(self) -> None:
        """Инициализирует объект камня."""
        self.position = self.randomize_position()
        positions.append(self.position)
        self.body_color = STONE_COLOR


class Snake(GameObject):
    """Описание абстракции змейки на игровом поле."""

    def __init__(self) -> None:
        """
        Присваивает экземпляру змейки все необходимые атрибуты.
        Атрибуты змейки, яблока и камня нужны для дальнейшего сброса.
        """
        super().__init__()
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.HEAD_POSITION = 0
        self.last = self.positions[-1]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Двигает змейку относительно направления движения."""
        head_coordinates = self.get_head_position()
        if self.direction in [RIGHT, LEFT]:
            step = GRID_SIZE * self.direction[0]
            self.positions.insert(
                self.HEAD_POSITION, (head_coordinates[0]
                                     + step, head_coordinates[1])
            )
        elif self.direction in [UP, DOWN]:
            step = GRID_SIZE * self.direction[1]
            self.positions.insert(
                self.HEAD_POSITION, (head_coordinates[0],
                                     head_coordinates[1] + step)
            )
        if len(self.positions) > self.length:
            self.positions.pop()

        self.delete_last_element()

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        head_rect = pygame.Rect(
            self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def delete_last_element(self):
        """Закрашивает последний элемент хвоста змейки."""
        last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        self.last = self.positions[-1]

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[self.HEAD_POSITION]

    def reset(self):
        """Сбрасывает всю змейку и ставит ей начальные координаты."""
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def conflicted_with_apple(self, apple):
        """Проверка на столкновение с яблоком."""
        if self.get_head_position() == apple.position:
            return True
        return False

    def conflicted_with_poisoned_food(self, poisoned_food):
        """Проверка на столкновение с отравленной едой."""
        if self.get_head_position() == poisoned_food.position:
            return True
        return False

    def conflicted_with_stone(self, stone):
        """Проверка на столкновение с камнем."""
        if self.get_head_position() == stone.position:
            return True
        return False

    def conflicted_with_tail(self):
        """Проверка на столкновение с хвостом."""
        for position in self.positions[1:]:
            if self.get_head_position() == position:
                return True
        return False

    def process_conflict_with_apple(self, apple):
        """Обрабатывает столкновение с яблоком."""
        self.length += 1
        apple.position = apple.randomize_position()

    def process_conflict_with_tail(self):
        """Обрабатывает столкновение змейки со своим хвостом (телом)."""
        self.reset()

    def process_conflict_with_borders(self):
        """Обрабатывает столкновение с границами игры."""
        head_position = self.get_head_position()
        if head_position[0] >= SCREEN_WIDTH or head_position[0] <= 0:
            self.positions[self.HEAD_POSITION] = (
                head_position[0] % SCREEN_WIDTH,
                head_position[1],
            )
        elif head_position[1] >= SCREEN_HEIGHT or head_position[1] <= 0:
            self.positions[self.HEAD_POSITION] = (
                head_position[0],
                head_position[1] % SCREEN_HEIGHT,
            )

    def process_conflict_with_stone(self, stone):
        """Обрабатывает столкновение с камнем."""
        self.reset()
        stone.position = stone.randomize_position()

    def process_conflict_with_poisoned_food(self, poisoned_food):
        """Обрабатывает столкновение с ядовитой едой."""
        if self.length == 1:
            self.reset()
        else:
            self.length -= 1
            self.positions.pop()
            self.delete_last_element()
        poisoned_food.position = poisoned_food.randomize_position()


def handle_keys(game_object):
    """Обрабатывает входящие события по мере действия игры."""
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
    """Основная функция игры. Создаются экземпляры класса змейки и яблока."""
    pygame.init()
    pygame.font.init()
    pygame.display.update()
    apple = Apple()
    poisoned_food = PoisonedFood()
    stone = Stone()
    snake = Snake()

    game_font = pygame.font.SysFont("Times New Roman", 24)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        if snake.conflicted_with_apple(apple):
            snake.process_conflict_with_apple(apple)
        elif snake.conflicted_with_poisoned_food(poisoned_food):
            if snake.length == 1:
                snake.process_conflict_with_poisoned_food(poisoned_food)
                apple.update_position()
                stone.update_position()
            else:
                snake.process_conflict_with_poisoned_food(poisoned_food)
        elif snake.conflicted_with_stone(stone):
            snake.process_conflict_with_stone(stone)
            apple.update_position()
            poisoned_food.update_position()
        elif snake.conflicted_with_tail():
            snake.process_conflict_with_tail()
            apple.update_position()
            stone.update_position()
            poisoned_food.update_position()
        snake.process_conflict_with_borders()

        while len(set(positions)) != len(positions):
            """
            Проверка на соответствие кооридинат объектов яблока,
            камня и ядовитой еды. Если координаты совпадают хоть двух объектов
            совпадают - все объекты принимают разные позиции. Также сделано
            для регулярного обновления экрана.
            """
            positions.clear()
            apple.position = apple.randomize_position()
            stone.position = stone.randomize_position()
            poisoned_food.position = poisoned_food.randomize_position()
            positions.append(apple.position)
            positions.append(stone.position)
            poisoned_food.append(poisoned_food.position)

        screen.fill(BOARD_BACKGROUND_COLOR)  # Заливаем фоном
        stone.draw()  # Отрисовываем все по новой, чтобы текст не накладывался
        snake.move()
        snake.draw()
        poisoned_food.draw()
        apple.draw()
        text_message = game_font.render(
            f"Score: {snake.length}", True, (0, 255, 0))
        screen.blit(
            text_message, (SCREEN_WIDTH // 2
                           - text_message.get_width() // 2, 0)
        )
        pygame.display.update()


if __name__ == "__main__":
    main()
