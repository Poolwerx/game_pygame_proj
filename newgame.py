import pygame
import sys
import os

pygame.init()
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
              'door': load_image('150door.png'),
              'trap_gold': load_image('150fake_gold_trap.png')}
immunity_hero = load_image('shield.png')
character_abilities = {'warrior': ['Воин ставит свой большой щит. Он блокирует весь урон!',
                                   'Чтобы узнать о статусе способности - около иконки пер-',
                                   'сонажа будет стоять щит. Действует 2 хода игрока.'],
                       'mage': ['Маг обладает магическими способностями - с помощью их',
                                'он может перещаться в пространстве через стенки и вра',
                                'гов. Перемещение происходит по направлению игрока.'],
                       'rogue': ['', '', '']}
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
    new_player, mushrooms, key_for_door, x, y = None, None, None, None, None
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
                mushrooms = Mushrooms('mushroom', x, y)
            elif level[y][x] == '/':
                Tile('empty', x, y)
                Tile('door', x, y)
            elif level[y][x] == '?':
                Tile('empty', x, y)
                key_for_door = Key_(x, y)
            elif level[y][x] == 'g':
                Tile('empty', x, y)
                Tile('trap_gold', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    return new_player, mushrooms, key_for_door, x, y


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
        self.hp_bar = 10
        self.immunity = 0
        self.position_hero_in_world = 'right'
        self.dop_pos_in_world = 'вправо'
        self.image = warrior_image
        self.key = False
        self.cooldown_abilities = 5
        self.cooldown_switch_hero = 5
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

        self.add(hero_group, all_sprites)

    def move_pers(self, movement):
        x, y = self.pos
        if self.cooldown_switch_hero != 0:
            self.cooldown_switch_hero -= 1
        if self.cooldown_abilities != 0:
            self.cooldown_abilities -= 1
        if self.immunity != 0:
            self.immunity -= 1
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
                self.dop_pos_in_world = 'наверх'
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
                self.dop_pos_in_world = 'вниз'
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
                self.dop_pos_in_world = 'влево'
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
                self.dop_pos_in_world = 'вправо'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)

    def switch_hero(self):
        if self.cooldown_switch_hero == 0:
            if self.class_hero == 'warrior':
                self.class_hero = 'mage'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
                self.hp_bar = 10
            elif self.class_hero == 'mage':
                self.class_hero = 'rogue'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
                self.hp_bar = 10
            elif self.class_hero == 'rogue':
                self.class_hero = 'warrior'
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
                self.hp_bar = 10
            self.cooldown_switch_hero = 5
            self.cooldown_abilities = 5

    def ability(self):
        if self.cooldown_abilities == 0:
            if self.class_hero == 'warrior':
                self.immunity = 2
            elif self.class_hero == 'mage':
                x, y = self.pos
                if self.dop_pos_in_world == 'вправо':
                    if level_map[y][x + 3] == '/' and self.key is True:
                        terminate()
                    if x >= 0 and (
                            level_map[y][x + 3] == '.' or level_map[y][x + 3] == ',' or level_map[y][x + 3] == '?'):
                        if level_map[y][x + 3] == '?':
                            key_for_door.transform()
                            self.key = True
                        self.rect = self.rect.move(+450, 0)
                        new_x, new_y = self.pos[0] + 3, self.pos[1]
                        self.pos = (new_x, new_y)
                elif self.dop_pos_in_world == 'влево':
                    if level_map[y][x - 3] == '/' and self.key is True:
                        terminate()
                    if x >= 0 and (
                            level_map[y][x - 3] == '.' or level_map[y][x - 3] == ',' or level_map[y][x - 3] == '?'):
                        if level_map[y][x - 1] == '?':
                            key_for_door.transform()
                            self.key = True
                        self.rect = self.rect.move(-450, 0)
                        new_x, new_y = self.pos[0] - 3, self.pos[1]
                        self.pos = (new_x, new_y)
                elif self.dop_pos_in_world == 'наверх':
                    if level_map[y - 3][x] == '/' and self.key is True:
                        terminate()
                    if y > 0 and (
                            level_map[y - 3][x] == '.' or level_map[y - 3][x] == ',' or level_map[y - 3][x] == '?'):
                        if level_map[y - 3][x] == '?':
                            key_for_door.transform()
                            self.key = True
                        self.rect = self.rect.move(0, -450)
                        new_x, new_y = self.pos[0], self.pos[1] - 3
                        self.pos = (new_x, new_y)
                elif self.dop_pos_in_world == 'вниз':
                    if level_map[y + 3][x] == '/' and self.key is True:
                        terminate()
                    if y > 0 and (
                            level_map[y + 3][x] == '.' or level_map[y + 3][x] == ',' or level_map[y + 3][x] == '?'):
                        if level_map[y + 3][x] == '?':
                            key_for_door.transform()
                            self.key = True
                        self.rect = self.rect.move(0, +450)
                        new_x, new_y = self.pos[0], self.pos[1] + 3
                        self.pos = (new_x, new_y)
            elif self.class_hero == 'rogue':
                print(1)
            self.cooldown_abilities = 7


class Mushrooms(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)
        self.add(mushroom_group, all_sprites)

    def check_pos_hero(self):
        pos_new10, pos_new11 = self.pos[0] + 1, self.pos[1]
        pos_new20, pos_new21 = self.pos[0] - 1, self.pos[1]
        pos_new30, pos_new31 = self.pos[0], self.pos[1] + 1
        pos_new40, pos_new41 = self.pos[0], self.pos[1] - 1
        pos_hero_1 = (pos_new10, pos_new11)
        pos_her_2 = (pos_new20, pos_new21)
        pos_hero_3 = (pos_new30, pos_new31)
        pos_hero_4 = (pos_new40, pos_new41)
        if pos_hero_1 == hero.pos or pos_her_2 == hero.pos or pos_hero_3 == hero.pos or pos_hero_4 == hero.pos:
            hero.hp_bar -= 3
            if hero.hp_bar <= 0:
                print(1)


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


def help_screen(class_her, health_bar, pos_in_wrld, cooldown_abil, cooldown_switch, immunity_her):
    fon = pygame.transform.scale(load_image('background.png'), size)
    font_for_class_hero = pygame.font.SysFont('century', 60)
    font_normal_text = pygame.font.SysFont('century', 35)
    hero_class_color = pygame.Color('white')
    name_of_hero = ''
    if cooldown_abil == 0:
        ability_hero_cooldown = 'Способность игрока готова к применению'
    else:
        if cooldown_abil == 1:
            ability_hero_cooldown = 'Откат способности через - ' + str(cooldown_abil) + ' ход'
        elif cooldown_abil > 4:
            ability_hero_cooldown = 'Откат способности через - ' + str(cooldown_abil) + ' ходов'
        else:
            ability_hero_cooldown = 'Откат способности через - ' + str(cooldown_abil) + ' хода'
    if cooldown_switch == 0:
        switch_hero_cooldown = 'Возможна смена героя'
    else:
        if cooldown_switch == 1:
            switch_hero_cooldown = 'Смена героя возможна через - ' + str(cooldown_switch) + ' ход'
        elif cooldown_switch > 4:
            switch_hero_cooldown = 'Смена героя возможна через - ' + str(cooldown_switch) + ' ходов'
        else:
            switch_hero_cooldown = 'Смена героя возможна через - ' + str(cooldown_switch) + ' хода'
    health_of_hero = 'Здоровье игрока ' + '(' + str(health_bar) + ')' + ' -'
    hp_bar = ''
    direction_of_movement = 'Направление движения и способностей игрока - ' + pos_in_wrld
    for i in range(health_bar):
        hp_bar += '/'
    if class_her == 'warrior':
        name_of_hero = '- воин'
        hero_class_color = pygame.Color('red')
    elif class_her == 'mage':
        name_of_hero = '- маг'
        hero_class_color = pygame.Color('blue')
    elif class_her == 'rogue':
        name_of_hero = '- вор'
        hero_class_color = pygame.Color('green')
    hero_class_txt = font_for_class_hero.render(name_of_hero, True, hero_class_color)
    health_txt = font_normal_text.render(health_of_hero, True, pygame.Color('white'))
    health_bar_txt = font_normal_text.render(hp_bar, True, pygame.Color('red'))
    direction_of_movement_txt = font_normal_text.render(direction_of_movement, True, pygame.Color('white'))
    ability_hero_cooldown_txt = font_normal_text.render(ability_hero_cooldown, True, pygame.Color('white'))
    switch_hero_cooldown_txt = font_normal_text.render(switch_hero_cooldown, True, pygame.Color('white'))
    spacer_txt = font_normal_text.render('______________________________________________________',
                                         True, pygame.Color('white'))
    screen.blit(fon, (0, 0))
    her_image = load_image('150' + class_her + '_' + 'right' + format_image)
    her_immunity_image = immunity_hero
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                return
        screen.blit(pygame.transform.scale(her_image, [230, 230]), [10, 10])
        if immunity_her != 0:
            screen.blit(pygame.transform.scale(her_immunity_image, [80, 70]), [300, 150])
        b = 550
        for i in range(3):
            txt_character_abilities = font_normal_text.render(character_abilities[class_her][i], True,
                                                              pygame.Color('white'))
            screen.blit(txt_character_abilities, (10, b))
            b += 50
        screen.blit(hero_class_txt, (270, 50))
        screen.blit(health_txt, (10, 250))
        screen.blit(health_bar_txt, (400, 250))
        screen.blit(direction_of_movement_txt, (10, 300))
        screen.blit(ability_hero_cooldown_txt, (10, 350))
        screen.blit(switch_hero_cooldown_txt, (10, 400))
        screen.blit(spacer_txt, (0, 500))
        pygame.display.flip()


def start_window():
    fon = pygame.transform.scale(load_image('start_window.jpg'), size)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


all_sprites = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
mushroom_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
level_map = load_level("map1.txt")
hero, mushrooms, key_for_door, level_x, level_y = generate_level(level_map)
camera = Camera()
running = True
start_window()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or \
                    event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE or event.key == pygame.K_e:
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
                if event.key == pygame.K_e:
                    hero.ability()
                mushrooms.check_pos_hero()
            if event.key == pygame.K_ESCAPE:
                help_screen(hero.class_hero, hero.hp_bar, hero.dop_pos_in_world, hero.cooldown_abilities,
                            hero.cooldown_switch_hero, hero.immunity)
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
