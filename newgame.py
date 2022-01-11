import pygame
import sys
import os

size = width, height = (1350, 750)
format_image = '.png'
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 60


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


tile_image = {'wall': load_image('150wall.png'),
              'empty': load_image('150floor.png'),
              'empty2': load_image('150floor_with_rocks.png'),
              'mushroom': load_image('150mushroom.png'),
              'key': load_image('150key.png'),
              'door': load_image('150door.png')}
warrior_image = load_image('150warrior_right.png')
mage_image = load_image('150mage_right.png')
rogue_image = load_image('150rogue_right.png')
tile_width = tile_height = 150


def terminate():
    pygame.quit()
    sys.exit()


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for inet in self:
            inet.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


def load_level(filename):
    filename = 'data/' + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))
    except FileNotFoundError:
        print('ERROR: нет такой карты или указано несуществующее название '
              'карты - укажите карту с типом файла через точку -> пример map.txt)')


def generate_level(level):
    new_player, key_for_door, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == ',':
                Tile('empty2', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
                Mushrooms('mushroom', x, y)
            elif level[y][x] == '/':
                Tile('empty', x, y)
                Tile('door', x, y)
            elif level[y][x] == '?':
                Tile('empty', x, y)
                key_for_door = Key_(x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    return new_player, key_for_door, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group, all_sprites)
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(sprite_group, all_sprites)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.class_hero = 'warrior'
        self.position_hero_in_world = 'right'
        self.image = warrior_image
        self.key = False
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)
        self.add(hero_group, all_sprites)

    def move_pers(self, movement):
        x, y = self.pos
        if movement == 'up':
            if level_map[y - 1][x] == '/' and self.key is True:
                terminate()
            if y > 0 and (level_map[y - 1][x] == '.' or level_map[y - 1][x] == ',' or level_map[y - 1][x] == '?'):
                if level_map[y - 1][x] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(0, -150)
                new_x, new_y = self.pos[0], self.pos[1] - 1
                self.pos = (new_x, new_y)
        elif movement == 'down':
            if level_map[y + 1][x] == '/' and self.key is True:
                terminate()
            if y > 0 and (level_map[y + 1][x] == '.' or level_map[y + 1][x] == ',' or level_map[y + 1][x] == '?'):
                if level_map[y + 1][x] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(0, +150)
                new_x, new_y = self.pos[0], self.pos[1] + 1
                self.pos = (new_x, new_y)
        elif movement == 'left':
            if level_map[y][x - 1] == '/' and self.key is True:
                terminate()
            if x >= 0 and (level_map[y][x - 1] == '.' or level_map[y][x - 1] == ',' or level_map[y][x - 1] == '?'):
                if level_map[y][x - 1] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(-150, 0)
                new_x, new_y = self.pos[0] - 1, self.pos[1]
                self.pos = (new_x, new_y)
                self.position_hero_in_world = 'left'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
        elif movement == 'right':
            if level_map[y][x + 1] == '/' and self.key is True:
                terminate()
            if x >= 0 and (level_map[y][x + 1] == '.' or level_map[y][x + 1] == ',' or level_map[y][x + 1] == '?'):
                if level_map[y][x + 1] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(+150, 0)
                new_x, new_y = self.pos[0] + 1, self.pos[1]
                self.pos = (new_x, new_y)
                self.position_hero_in_world = 'right'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)

    def switch_hero(self):
        if self.class_hero == 'warrior':
            self.class_hero = 'mage'
            self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
        elif self.class_hero == 'mage':
            self.class_hero = 'rogue'
            self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
        elif self.class_hero == 'rogue':
            self.class_hero = 'warrior'
            self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)


class Mushrooms(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(mushroom_group, all_sprites)


class Key_(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = tile_image['key']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(key_group, all_sprites)

    def transform(self):
        self.image = tile_image['empty']


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


all_sprites = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
mushroom_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
level_map = load_level("map1.txt")
hero, key_for_door, level_x, level_y = generate_level(level_map)
camera = Camera()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                hero.move_pers('up')
            if event.key == pygame.K_DOWN:
                hero.move_pers('down')
            if event.key == pygame.K_LEFT:
                hero.move_pers('left')
            if event.key == pygame.K_RIGHT:
                hero.move_pers('right')
            if event.key == pygame.K_SPACE:
                hero.switch_hero()
            if event.key == pygame.K_ESCAPE:
                print('1')
    camera.update(hero)
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill(pygame.Color(0, 0, 0))
    sprite_group.draw(screen)
    mushroom_group.draw(screen)
    key_group.draw(screen)
    hero_group.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
terminate()
