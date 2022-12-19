from random import randint


class FieldException(Exception):
    pass


class FieldOutException(FieldException):
    """выход за пределы поля"""

    def __str__(self):
        return 'Выстрел за пределы поля'


class FieldUsedException(FieldException):
    """точка уже занята"""

    def __str__(self):
        return 'В эту точку уже стреляли'


class FieldWrongShipException(FieldException):
    """ошибка размещения корабля"""
    pass


class Dot:
    """класс точек на поле, их сравнение и вывод в консоль"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class Ship:
    """класс создания кораблей и проверки попаданий"""

    def __init__(self, bow, liv, o):
        self.bow = bow
        self.liv = liv
        self.o = o
        self.lives = liv

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.liv):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Field:
    """Поле, корабли, контур, выстрелы и попадания"""

    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = '  | '
        for i in range(1, self.size + 1):
            res += f'{i} | '
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' | '

        if self.hid:
            res = res.replace('■', 'O')
        return res

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise FieldWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise FieldOutException()

        if d in self.busy:
            raise FieldUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    """ класс игрока"""

    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BaseException as e:
                print(e)


class AI(Player):
    """игрок компьютер"""

    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")

        return d


class User(Player):
    """игрок пользователь"""

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    """конструктор игры, генерация поля и размещение кораблей, приветствие и мануал, консольный интерфейс"""

    def __init__(self, size=6):
        self.size = size
        pl = self.random_field()
        co = self.random_field()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_field(self):
        field = None
        while field is None:
            field = self.random_place()
        return field

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = Field(size=self.size)
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    field.add_ship(ship)
                    break
                except FieldWrongShipException:
                    pass
        field.begin()
        return field

    @staticmethod
    def greet():
        print("-------------------")
        print("  Добро пожаловать  ")
        print("      в игру       ")
        print("    морской бой!    ")
        print(" да начнется битва! ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Поле игрока:")
            print(self.us.field)
            print("-" * 20)
            print("Поле компьютера:")
            print(self.ai.field)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.field.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.field.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
