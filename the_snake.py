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

    def paint_over(self, position):
        """Закрашивает клетку на определенной позиции."""
        rect = pygame.Rect(position,
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


class EatableObject(GameObject):
    """Описывает абстракцию еды на поле."""

    def __init__(self, body_color=APPLE_COLOR) -> None:
        """Инициализирует объект еды."""
        super().__init__(body_color=body_color)

    def generate_random_position(self):
        """Возвращает случайную позицию."""
        return (randrange(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE),
                randrange(0, GRID_HEIGHT * GRID_SIZE,
                          GRID_SIZE))

    def randomize_position(self, positions):
        """Устанавливает объекту случайную позицию."""
        all_positions = positions.copy()
        all_positions.pop(self.get_name())
        random_coordinate = self.generate_random_position()
        position_x, position_y = random_coordinate
        while ((position_x, position_y) in positions['snake']
               or (position_x, position_y) in all_positions.values()):
            position_x, position_y = self.generate_random_position()
        self.position = (position_x, position_y)
        positions[self.get_name()] = self.position

    def draw(self):
        """
        Рисует клетку (метод родителя, принцип один и тот же во всех классах
        потомках, без переопределения в наследниках).
        """
        head_rect = pygame.Rect(self.position,
                                (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)


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
        """Присваивает экземпляру змейки все необходимые атрибуты."""
        super().__init__(body_color=SNAKE_COLOR)
        self.set_default_attributes()

    def set_default_attributes(self):
        """Устанавливает начальные атрибуты змейке."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.last = None

    def update_direction(self, direction):
        """Обновляет направление движения змейки."""
        self.direction = direction

    def move(self):
        """Двигает змейку относительно направления движения."""
        head_coordinates = self.get_head_position()
        step = [x * GRID_SIZE for x in self.direction]
        step_x, step_y = step
        position_x, position_y = head_coordinates[0], head_coordinates[1]
        new_head_position = ((position_x + step_x) % SCREEN_WIDTH,
                             (position_y + step_y) % SCREEN_HEIGHT)
        self.positions.insert(0, new_head_position)

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        head_rect = pygame.Rect(self.get_head_position(),
                                (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            self.paint_over(self.last)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает всю змейку и ставит ей начальные координаты."""
        for position in self.positions:
            rect = pygame.Rect(position,
                               (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
        self.set_default_attributes()
        self.direction = choice([RIGHT, LEFT, UP, DOWN])


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

    """
    Локальная переменная для хранения позиций объектов для
    дальнейшего сравнения в randomize_position().
    """
    positions = {

    }

    # Передаем в инициализатор позиции объектов для дальнейшего сравнивания
    snake = Snake()
    apple = Apple()  # Передается локальная переменная positions
    poisoned_food = PoisonedFood(POISONED_FOOD_COLOR)
    stone = Stone(STONE_COLOR)  # Необходимый первый аргумент

    positions['snake'] = snake.positions
    positions['apple'] = apple.position
    positions['stone'] = stone.position
    positions['poisoned_food'] = poisoned_food.position

    apple.randomize_position(positions)
    stone.randomize_position(positions)
    poisoned_food.randomize_position(positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.move()
        snake.draw()
        apple.draw()
        poisoned_food.draw()
        stone.draw()
        snake_head = snake.get_head_position()

        positions['snake'] = snake.positions

        if snake_head == apple.position:
            apple.randomize_position(positions)
            snake.length += 1
            snake.draw()
        elif snake_head == poisoned_food.position:
            if snake.length == 1:
                reset_objects(apple, stone, snake=snake)
            else:
                snake.length -= 1
                snake.draw()
            poisoned_food.randomize_position(positions)
        elif snake_head == stone.position:
            reset_objects(positions, apple, stone, poisoned_food, snake=snake)
        elif snake_head in snake.positions[1:]:
            reset_objects(positions, apple, stone, poisoned_food, snake=snake)
        pygame.display.update()


def reset_objects(positions, *args, snake=None):
    """Сбрасывает объекты."""
    if snake:
        snake.reset()
        # Сбрасываем змейку, иначе ничего не делаем
        positions['snake'] = snake.positions
    for object in args:
        object.paint_over(object.position)
        object.randomize_position(positions)


if __name__ == "__main__":
    main()
