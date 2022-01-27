import pygame
import sys
import os

# ФПС игры + размер окна игры  + переменная за подсчет уровней
pygame.init()
size = width, height = (1350, 750)
format_image = '.png'
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 60
level_count = 1
count_moves = 0
count_ability = 0
count_switch_hero = 0


# функция загрузки изображений
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


# функция для подстановки в правильную форму сущ
def correct_form_noun(numb, arg):
    noun = []
    if arg == 'moves':
        noun = ['ход', 'хода', 'ходов']
    elif arg == 'ability':
        noun = ['способность', 'способности', 'способностей']
    if numb % 10 == 1 and numb % 100 != 11:
        p = 0
    elif 2 <= numb % 10 <= 4 and (numb % 100 < 10 or numb % 100 >= 20):
        p = 1
    else:
        p = 2
    if arg == 'moves':
        if p == 0 and arg == 'moves':
            return 'Сделан ' + str(numb) + ' ' + noun[p]
        return 'Сделано ' + str(numb) + ' ' + noun[p]
    else:
        if p == 0:
            return 'Использована ' + str(numb) + ' ' + noun[p]
        return 'Использовано ' + str(numb) + ' ' + noun[p]


# функция сохр. результатов в текстовый файл
def write_results(points, game_level_count, game_count_moves, all_count_ability):
    all_result = str(points + ' // ' + game_level_count + ' // ' + game_count_moves + ' // ' + all_count_ability)
    with open("results.txt", "a") as file:
        file.write('\n' + str(all_result))


# словарь с картинками тайлов - нужен для загрузки
tile_image = {'wall': load_image('150wall.png'),
              'empty': load_image('150floor.png'),
              'empty2': load_image('150floor_with_rocks.png'),
              'mushroom': load_image('150mushroom.png'),
              'key': load_image('150key.png'),
              'door': load_image('150door.png'),
              'trap_gold': load_image('150fake_gold_trap.png'),
              'freezing_trap': load_image('150freezing_trap.png'),
              'blue_mushroom': load_image('150blue_mushroom.png')}
immunity_hero = load_image('shield.png')
# словарь с описанием способностей персонажа - нужен для вспомогательного окна
character_abilities = {'warrior': ['Воин ставит свой большой щит. Он блокирует весь урон! Чтобы узнать о стату-',
                                   'се способности - около иконки персонажа появится щит - действует 2 хода игро-',
                                   'ка (используйте в критические моменты либо для обхода врагов).'],
                       'mage': ['Маг обладает магическими способностями - с помощью их, он может перещать-',
                                'ся в пространстве на 2 игровых поля (способность работает через препят -',
                                'ствия. Перемещение способностью происходит по направлению игрока.'],
                       'rogue': ['Вор, плут, авантюрист - называйте его как хотите, у вора нет активных способ-',
                                 'ностей, но обладает большим даром - он может без всяких трудностей стащить',
                                 'у врага из под носа гору монет (так же на вора не действуют никакие ловушки).']}
# загрузка картинок персонажей
warrior_image = load_image('150warrior_right.png')
mage_image = load_image('150mage_right.png')
rogue_image = load_image('150rogue_right.png')

icecle_image = load_image('150icecle.png')
broke_icecle_image = load_image('150icecle2.png')
tile_width = tile_height = 150

# дериктория музыки и звуков игры
music_dir = os.path.join(os.path.dirname(__file__), 'data_music')
sound_dir = os.path.join(os.path.dirname(__file__), 'data_sounds')

# загрузка звуков игры + настройка их громкости
move_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'move.wav'))
door_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'door.wav'))
ice_broking_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'ice_broking.wav'))
mushroom_attack_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'mushroom_attack.wav'))
swipe_hero_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'swing.wav'))
mage_blink_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'blink.wav'))
money_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'money.wav'))
money_attack_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'gold_attack.wav'))
immunity_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'immyniti.wav'))

move_sound.set_volume(0.1)
door_sound.set_volume(0.2)
mushroom_attack_sound.set_volume(0.2)
swipe_hero_sound.set_volume(0.2)
mage_blink_sound.set_volume(0.1)
money_sound.set_volume(0.2)
money_attack_sound.set_volume(0.1)

mushrooms = []


# выход из цикла
def terminate():
    pygame.quit()
    sys.exit()


# загрузка карты из текст. файла - преобразование в список
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


# генерация уровня
def generate_level(level):
    new_player, key_for_door, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 'f':
                Tile('empty', x, y)
                Tile('freezing_trap', x, y)
            elif level[y][x] == ',':
                Tile('empty2', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
                Mushrooms('mushroom', x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                Blue_mushrooms('blue_mushroom', x, y)
                level[y][x] = '.'
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
    return new_player, key_for_door, x, y


# класс тайла
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group, all_sprites)
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(sprite_group, all_sprites)


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        # класс игрока
        self.class_hero = 'warrior'
        # здоровье игрока
        self.hp_bar = 10
        # статус заморожен или нет
        self.frozen = 0
        # счетчик ходов
        self.count_moves = 0
        # статус иммунитета урона - для способности воина
        self.immunity = 0
        # направление способностей
        self.position_hero_in_world = 'right'
        self.dop_pos_in_world = 'вправо'
        # изображение игрока
        self.image = warrior_image
        self.key = False
        self.stop = 0
        self.cooldown_abilities = 5
        self.cooldown_switch_hero = 5
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

        self.add(hero_group, all_sprites)

    # функция движения игрока
    def move_pers(self, movement):
        global count_moves
        count_moves += 1
        # позиция игрока по x и y
        x, y = self.pos
        # вычисление кулдаунов
        if self.cooldown_switch_hero != 0:
            self.cooldown_switch_hero -= 1
        if self.cooldown_abilities != 0:
            self.cooldown_abilities -= 1
        if self.immunity != 0:
            self.immunity -= 1
        # проверка статуса заморожен/не заморожен
        if self.frozen != 0:
            ice_broking_sound.play()
            self.frozen -= 1
            if self.frozen == 1:
                self.image = broke_icecle_image
                return
            elif self.frozen == 0:
                self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
        # проверка если движение вверх
        if movement == 'up':
            # проверка тайла на дверь
            if level_map[y - 1][x] == '/' and self.key is True:
                door_sound.play()
                # остоновка уровня
                self.stop += 1
                return
            # проверка на тайл - если не дверь и не стена + гриб
            if y > 0 and (level_map[y - 1][x] == '.' or level_map[y - 1][x] == ',' or level_map[y - 1][x] == '?' or
                          level_map[y - 1][x] == 'g' or level_map[y - 1][x] == 'f'):
                # проверка на ловушку
                if level_map[y - 1][x] == 'g' and hero.class_hero != 'rogue':
                    money_attack_sound.play()
                    self.stop += 20
                # проверка на ловушку и класс героя - вор
                elif level_map[y - 1][x] == 'g' and hero.class_hero == 'rogue':
                    money_sound.play()
                # если тайл ключ
                if level_map[y - 1][x] == '?':
                    key_for_door.transform()
                    self.key = True
                # перемещение игрока на нужный тайл
                self.rect = self.rect.move(0, -150)
                # новая позиция игрока
                new_x, new_y = self.pos[0], self.pos[1] - 1
                # запись в позицию игрока
                self.pos = (new_x, new_y)
                # задача на новую позицию игрока
                self.dop_pos_in_world = 'наверх'
        elif movement == 'down':
            if level_map[y + 1][x] == '/' and self.key is True:
                door_sound.play()
                self.stop += 1
            if y > 0 and (level_map[y + 1][x] == '.' or level_map[y + 1][x] == ',' or level_map[y + 1][x] == '?' or
                          level_map[y + 1][x] == 'g' or level_map[y + 1][x] == 'f'):
                if level_map[y + 1][x] == 'g' and hero.class_hero != 'rogue':
                    money_attack_sound.play()
                    self.stop += 20
                    return
                elif level_map[y + 1][x] == 'g' and hero.class_hero == 'rogue':
                    money_sound.play()
                if level_map[y + 1][x] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(0, +150)
                new_x, new_y = self.pos[0], self.pos[1] + 1
                self.pos = (new_x, new_y)
                self.dop_pos_in_world = 'вниз'
        elif movement == 'left':
            if level_map[y][x - 1] == '/' and self.key is True:
                door_sound.play()
                self.stop += 1
            if x >= 0 and (level_map[y][x - 1] == '.' or level_map[y][x - 1] == ',' or level_map[y][x - 1] == '?' or
                           level_map[y][x - 1] == 'g' or level_map[y][x - 1] == 'f'):
                if level_map[y][x - 1] == 'g' and hero.class_hero != 'rogue':
                    money_attack_sound.play()
                    self.stop += 20
                    return
                elif level_map[y][x - 1] == 'g' and hero.class_hero == 'rogue':
                    money_sound.play()
                if level_map[y][x - 1] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(-150, 0)
                new_x, new_y = self.pos[0] - 1, self.pos[1]
                self.pos = (new_x, new_y)
                self.position_hero_in_world = 'left'
                self.dop_pos_in_world = 'влево'
        elif movement == 'right':
            if level_map[y][x + 1] == '/' and self.key is True:
                door_sound.play()
                self.stop += 1
            if x >= 0 and (level_map[y][x + 1] == '.' or level_map[y][x + 1] == ',' or level_map[y][x + 1] == '?' or
                           level_map[y][x + 1] == 'g' or level_map[y][x + 1] == 'f'):
                if level_map[y][x + 1] == 'g' and hero.class_hero != 'rogue':
                    money_attack_sound.play()
                    self.stop += 20
                    return
                elif level_map[y][x + 1] == 'g' and hero.class_hero == 'rogue':
                    money_sound.play()
                if level_map[y][x + 1] == '?':
                    key_for_door.transform()
                    self.key = True
                self.rect = self.rect.move(+150, 0)
                new_x, new_y = self.pos[0] + 1, self.pos[1]
                self.pos = (new_x, new_y)
                self.position_hero_in_world = 'right'
                self.dop_pos_in_world = 'вправо'
        x, y = self.pos
        if level_map[y][x] == 'f' and self.frozen == 0 and self.class_hero != 'rogue':
            self.image = icecle_image
            self.frozen += 2
        else:
            self.image = load_image('150' + self.class_hero + '_' + self.position_hero_in_world + format_image)
            move_sound.play()
        self.count_moves += 1

    # функция смены персонажа - меняет класс героя + (изображение героя и обновляет кулдауны смены героя)
    def switch_hero(self):
        global count_switch_hero
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
            swipe_hero_sound.play()
            count_switch_hero += 1
            self.cooldown_switch_hero = 5
            self.cooldown_abilities = 5

    # способность игрока - зависит от класса игрока
    def ability(self):
        global count_ability
        if self.cooldown_abilities == 0:
            if self.class_hero == 'warrior':
                self.immunity = 3
            elif self.class_hero == 'mage':
                x, y = self.pos
                if self.dop_pos_in_world == 'вправо':
                    if level_map[y][x + 3] == '/' and self.key is True:
                        door_sound.play()
                        self.stop += 1
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
                        door_sound.play()
                        self.stop += 1
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
                        door_sound.play()
                        self.stop += 1
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
                        door_sound.play()
                        self.stop += 1
                    if y > 0 and (
                            level_map[y + 3][x] == '.' or level_map[y + 3][x] == ',' or level_map[y + 3][x] == '?'):
                        if level_map[y + 3][x] == '?':
                            key_for_door.transform()
                            self.key = True
                        self.rect = self.rect.move(0, +450)
                        new_x, new_y = self.pos[0], self.pos[1] + 3
                        self.pos = (new_x, new_y)
                mage_blink_sound.play()
            elif self.class_hero == 'rogue':
                money_sound.play()
            count_ability += 1
            self.cooldown_abilities = 7


# класс гриба противника
class Mushrooms(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        global mushrooms
        super().__init__()
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)
        mushrooms.append(self.pos)
        self.add(mushroom_group, all_sprites)

    # функция проверки позиции игрока рядом с грбом
    def check_pos_hero(self):
        global mushrooms
        for i in range(len(mushrooms)):
            pos_new10, pos_new11 = mushrooms[i][0] + 1, mushrooms[i][1]
            pos_new20, pos_new21 = mushrooms[i][0] - 1, mushrooms[i][1]
            pos_new30, pos_new31 = mushrooms[i][0], mushrooms[i][1] + 1
            pos_new40, pos_new41 = mushrooms[i][0], mushrooms[i][1] - 1
            pos_hero_1 = (pos_new10, pos_new11)
            pos_her_2 = (pos_new20, pos_new21)
            pos_hero_3 = (pos_new30, pos_new31)
            pos_hero_4 = (pos_new40, pos_new41)
            if pos_hero_1 == hero.pos or pos_her_2 == hero.pos or pos_hero_3 == hero.pos or pos_hero_4 == hero.pos:
                if hero.immunity == 0:
                    hero.hp_bar -= 3
                    mushroom_attack_sound.play()
                    if hero.hp_bar <= 0:
                        end_window(level_count, count_moves, count_ability, count_switch_hero)
                else:
                    immunity_sound.play()


# класс синего гриба
class Blue_mushrooms(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(blue_mushroom_group, all_sprites)


# класс ключа
class Key_(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = tile_image['key']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.add(key_group, all_sprites)

    def transform(self):
        self.image = tile_image['empty']


# класс камеры
class Camera:
    # начальный сдвиг камеры
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


# вспомогательное окно для игрока - помогает отслеживать позицию в мире и кулдаун способностей
def help_screen(class_her, health_bar, pos_in_wrld, cooldown_abil, cooldown_switch, immunity_her, key_her):
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
    if class_her == 'warrior' or class_her == 'mage':
        ability_hero_button = 'Применить способность на клавишу - "E"'
    else:
        ability_hero_button = 'У вора нет спобностей - даже не пытайтесь нажать на "E"'
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
    spacer_txt = font_normal_text.render('___________________________________________________________________________',
                                         True, pygame.Color('white'))
    ability_hero_button_txt = font_normal_text.render(ability_hero_button, True, pygame.Color('white'))
    about_escape_txt = font_normal_text.render('Для выхода из окна - нажатие любой клавиши', True,
                                               pygame.Color('white'))
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
        if key_her is True:
            screen.blit(pygame.transform.scale(tile_image['key'], [100, 130]), [450, 100])
        if immunity_her != 0:
            screen.blit(pygame.transform.scale(her_immunity_image, [80, 70]), [300, 150])
        b = 550
        for i in range(3):
            txt_character_abilities = font_normal_text.render(character_abilities[class_her][i], True,
                                                              pygame.Color('white'))
            screen.blit(txt_character_abilities, (5, b))
            b += 50
        screen.blit(hero_class_txt, (270, 50))
        screen.blit(health_txt, (10, 250))
        screen.blit(health_bar_txt, (400, 250))
        screen.blit(direction_of_movement_txt, (10, 300))
        screen.blit(ability_hero_cooldown_txt, (10, 350))
        screen.blit(switch_hero_cooldown_txt, (10, 400))
        screen.blit(ability_hero_button_txt, (10, 450))
        screen.blit(about_escape_txt, (10, 500))
        screen.blit(spacer_txt, (0, 515))
        pygame.display.flip()


# функция стартового окна
def start_window():
    pygame.mixer.music.load(os.path.join(music_dir, 'start_theme.mp3'))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)
    fon = pygame.transform.scale(load_image('start_window.jpg'), size)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


# функция финального окна
def end_window(level_count_, count_moves_, count_ability_, count_switch_hero_):
    pygame.mixer.music.load(os.path.join(music_dir, 'boys_cry.mp3'))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)
    fon = pygame.transform.scale(load_image('itog.jpg'), size)
    font_normal_text = pygame.font.SysFont('century', 50)
    if level_count_ == 3:
        level_count_txt = 'ИГРА ПРОЙДЕНА'
    else:
        level_count_txt = 'Уровень игры - ' + str(level_count_)
    count_moves_txt = correct_form_noun(count_moves_, 'moves')
    if count_ability_ == 0:
        count_ability_txt = 'Не использовано способностей'
    else:
        count_ability_txt = correct_form_noun(count_ability_, 'ability')
    if count_switch_hero_ == 1:
        count_switch_hero_txt = '       Использован игроком - воин и маг'
    elif count_switch_hero_ >= 2:
        count_switch_hero_txt = 'Использованы все персонажи - воин, маг, вор'
    else:
        count_switch_hero_txt = 'Игрок не использовал других персонажей'

    level_count_text = font_normal_text.render(level_count_txt, True, pygame.Color('white'))
    count_moves_text = font_normal_text.render(count_moves_txt, True, pygame.Color('white'))
    count_ability_text = font_normal_text.render(count_ability_txt, True, pygame.Color('white'))
    count_switch_hero_text = font_normal_text.render(count_switch_hero_txt, True, pygame.Color('white'))

    moves_score_points = 300 - (count_moves_ * 0.5)
    switch_score_points = 100 - (count_switch_hero_ * 5)
    ability_score_points = 100 - (count_ability_ * 5)
    if moves_score_points <= 0:
        moves_score_points = 0
    if switch_score_points <= 0:
        switch_score_points = 0
    if ability_score_points <= 0:
        ability_score_points = 0
    if level_count_ != 3:
        all_points = 'Игрок не прошел больше 2 уровней'
        all_points_txt = 'Игрок не прошел больше 2 уровней'
    else:
        all_points = 'Всего очков - ' + str(int(moves_score_points + switch_score_points + ability_score_points))
        all_points_txt = '               Всего очков - ' + \
                         str(int(moves_score_points + switch_score_points + ability_score_points))
    all_points_text = font_normal_text.render(all_points_txt, True, pygame.Color('orange'))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                write_results(all_points, level_count_txt, count_moves_txt, count_ability_txt)
                terminate()
        screen.blit(level_count_text, (470, 230))
        screen.blit(count_moves_text, (470, 290))
        screen.blit(count_ability_text, (325, 350))
        screen.blit(count_switch_hero_text, (200, 410))
        screen.blit(all_points_text, (250, 520))
        pygame.display.flip()


# группы спрайтов
all_sprites = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
mushroom_group = pygame.sprite.Group()
blue_mushroom_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()

# загрузка 1 уровня + камера + цикл
level_map = load_level("map1.txt")
hero, key_for_door, level_x, level_y = generate_level(level_map)
camera = Camera()
running = True
mushroom = Mushrooms('mushroom', 0, 0)


# цикл игры и загрузки уровней
def game_running():
    global level_count

    # главная функция игры
    def game_window():
        pygame.mixer.music.load(os.path.join(music_dir, 'ASIM_main_theme.mp3'))
        pygame.mixer.music.play(loops=-1)
        font = pygame.font.SysFont('century', 60)
        level_txt = 'Уровень - ' + str(level_count)
        pygame.mixer.music.set_volume(0.2)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if hero.stop != 0:
                    return
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
                        mushroom.check_pos_hero()
                    if event.key == pygame.K_ESCAPE:
                        help_screen(hero.class_hero, hero.hp_bar, hero.dop_pos_in_world, hero.cooldown_abilities,
                                    hero.cooldown_switch_hero, hero.immunity, hero.key)
            camera.update(hero)
            for sprite in all_sprites:
                camera.apply(sprite)
            screen.fill(pygame.Color(0, 0, 0))
            sprite_group.draw(screen)
            mushroom_group.draw(screen)
            key_group.draw(screen)
            hero_group.draw(screen)
            blue_mushroom_group.draw(screen)
            if hero.count_moves == 0:
                screen.blit(pygame.transform.scale(load_image('background.png'), [330, 80]), [0, 0])
                hero_class_txt = font.render(level_txt, True, pygame.Color('red'))
                screen.blit(hero_class_txt, (0, 0))
            pygame.display.flip()
            clock.tick(fps)

    # функция загрузки новых уровней и обнуления групп спрайтов + карты; и других значений
    def switch():
        global all_sprites, hero_group, sprite_group, key_group, mushroom_group, blue_mushroom_group
        global level_map, hero, mushrooms, key_for_door, level_x, level_y, camera
        global running, level_count
        all_sprites = pygame.sprite.Group()
        hero_group = pygame.sprite.Group()
        blue_mushroom_group = pygame.sprite.Group()
        sprite_group = pygame.sprite.Group()
        mushroom_group = pygame.sprite.Group()
        key_group = pygame.sprite.Group()
        level_map = ''
        if hero.stop > 10:
            level_map = load_level("map_trap.txt")
        elif level_count == 1:
            level_map = load_level("map2.txt")
            level_count += 1
        elif level_count == 2:
            level_map = load_level("map3.txt")
            level_count += 1
        hero.kill()
        running = True
        hero, key_for_door, level_x, level_y = None, None, None, None
        hero, key_for_door, level_x, level_y = generate_level(level_map)
        camera = Camera()

    # запуски игры и смены уровны (обнуления переменных)
    game_window()
    switch()
    game_window()
    switch()
    game_window()
    end_window(level_count, count_moves, count_ability, count_switch_hero)


# основной запуск игры и старт. окна
start_window()
game_running()
