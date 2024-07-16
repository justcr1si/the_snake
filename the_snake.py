from random import randrange, choice

import pygame
import pygame.freetype

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
SPEED = 20

# Цвет текста
TEXT_COLOR = (0, 255, 0)

# Окно игры
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Описание игры
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()

# Позиции объектов (для дальнейшего сравнивания в методе randomize_position())
positions = {
    'snake': [(0, 0)],
    'apple': (0, 0),
    'stone': (0, 0),
    'poisoned_food': (0, 0),
}


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


class EatableObject(GameObject):
    """Описывает абстракцию еды на поле."""

    def __init__(self, body_color=APPLE_COLOR) -> None:
        """Инициализирует объект еды."""
        self.randomize_position()
        self.body_color = body_color

    def get_name(self):
        """Абстрактный метод, возвращает название объекта."""
        pass

    def randomize_position(self):
        """
        Возвращает случайную позицию
        Проверяет новую позицию, чтобы она не была равна позиции остальных
        объектов.
        """
        all_positions = positions.copy()
        all_positions.pop(self.get_name())
        random_coordinate = (randrange(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE),
                             randrange(0, SCREEN_HEIGHT - GRID_SIZE,
                                       GRID_SIZE))
        x, y = random_coordinate
        while (x, y) in positions['snake'] or (x, y) in all_positions.values():
            x, y = (randrange(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE),
                    randrange(0, SCREEN_HEIGHT - GRID_SIZE,
                              GRID_SIZE))
        self.position = (x, y)

    def draw(self):
        """Рисует определенную ячейку."""
        rect = pygame.Rect(self.position,
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class PoisonedFood(EatableObject):
    """Описывает ядовитую еду."""

    def get_name(self):
        """Возвращает название объекта."""
        return 'poisoned_food'


class Apple(EatableObject):
    """
    Описывает абстракцию игрового яблока,
    который наследуется от GameObject.
    """

    def get_name(self):
        """Возвращает название объекта."""
        return 'apple'


class Stone(EatableObject):
    """Описывает абстракцию игрового камня."""

    def get_name(self):
        """Возвращает название объекта."""
        return 'stone'


class Snake(GameObject):
    """Описание абстракции змейки на игровом поле."""

    def __init__(self) -> None:
        """
        Присваивает экземпляру змейки все необходимые атрибуты.
        Атрибуты змейки, яблока и камня нужны для дальнейшего сброса.
        """
        super().__init__()
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.body_color = SNAKE_COLOR

    def update_direction(self, direction):
        """Обновляет направление движения змейки."""
        if direction in [RIGHT, LEFT, UP, DOWN]:
            self.direction = direction

    def move(self):
        """Двигает змейку относительно направления движения."""
        head_coordinates = self.get_head_position()
        if self.direction in [RIGHT, LEFT]:
            step = GRID_SIZE * self.direction[0]
            self.positions.insert(
                0, ((head_coordinates[0]
                     + step) % SCREEN_WIDTH,
                    head_coordinates[1])
            )
        elif self.direction in [UP, DOWN]:
            step = GRID_SIZE * self.direction[1]
            self.positions.insert(
                0, (head_coordinates[0],
                    (head_coordinates[1] + step)
                    % SCREEN_HEIGHT)
            )
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self, apple, poisoned_food, stone):
        """Сбрасывает всю змейку и ставит ей начальные координаты."""
        self.__init__()
        apple.randomize_position()
        poisoned_food.randomize_position()
        stone.randomize_position()


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
    """Основная функция игры. Создаются экземпляры класса змейки и яблока."""
    pygame.init()
    pygame.font.init()
    pygame.display.update()
    snake = Snake()
    apple = Apple()
    poisoned_food = PoisonedFood(POISONED_FOOD_COLOR)
    stone = Stone(STONE_COLOR)

    game_font = pygame.font.SysFont("Times New Roman", 24)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        screen.fill(BOARD_BACKGROUND_COLOR)  # Заливаем фоном
        snake.move()
        snake.draw()
        apple.draw()
        poisoned_food.draw()
        stone.draw()
        snake_head = snake.get_head_position()

        positions['snake'] = snake.positions
        positions['poisoned_food'] = poisoned_food.position
        positions['stone'] = stone.position
        positions['apple'] = apple.position

        if snake_head == apple.position:
            apple.randomize_position()
            snake.length += 1
        elif snake_head == poisoned_food.position:
            poisoned_food.randomize_position()
            if snake.length == 1:
                snake.reset(apple, poisoned_food, stone)
            else:
                snake.length -= 1
                snake.positions.pop()
        elif snake_head == stone.position:
            snake.reset(apple, poisoned_food, stone)
            snake.direction = choice([RIGHT, LEFT, UP, DOWN])
        for position in snake.positions[1:]:
            if snake_head == position:
                snake.reset(apple, poisoned_food, stone)

        text_message = game_font.render(
            f"Score: {snake.length}", True, (0, 255, 0))
        screen.blit(
            text_message, (SCREEN_WIDTH // 2
                           - text_message.get_width() // 2, 0)
        )
        pygame.display.update()


if __name__ == "__main__":
    main()
