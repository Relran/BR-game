import socket
import select
import pygame


class Player:
    def __init__(self, player_name):
        self.name = player_name
        self.color = ""
        self.x_person = 0
        self.y_person = 0
        self.position_string = "0 0"
        self.seconds = 0  # time not moved
        self.ammo = 3  # shoots left
        self.ammo_reagen = 0  # how much till add more ammo
        self.health = 90
        self.cursor = ""
        self.shoot = False

    def check_mouse_position(self):
        # tuple [0]=x [-1]=y
        self.cursor = ""

        if pygame.mouse.get_pos()[0] < 0:
            self.cursor = "0"
        elif pygame.mouse.get_pos()[0] > 560:
            self.cursor += "560"
        else:
            self.cursor = str(pygame.mouse.get_pos()[0])

        if pygame.mouse.get_pos()[-1] < 0:
            self.cursor += " 0"
        elif pygame.mouse.get_pos()[-1] > 560:
            self.cursor += " 560"
        else:
            self.cursor += " " + str(pygame.mouse.get_pos()[-1])

    def ammo_stuff(self):
        if self.ammo != 3:
            self.ammo_reagen += 1
            if self.ammo_reagen == 1000:
                self.ammo_reagen = 0
                self.ammo += 1

    def check_change_in_position(self):
        pressed_key = pygame.key.get_pressed()  # list of indicators for pressed keys
        key_index = 0
        not_moved = True
        for key in pressed_key:  # key=1 -> pressed. key=0 -> not pressed
            if key == 1:  # some key has been pressed
                if key_index == 26 and self.y_person >= -10:  # w => 26
                    self.y_person -= 1  # up
                    not_moved = False
                if key_index == 4 and self.x_person >= -10:  # a => 4
                    self.x_person -= 1  # left
                    not_moved = False
                if key_index == 22 and self.y_person <= 530:  # s => 22
                    self.y_person += 1  # down
                    not_moved = False
                if key_index == 7 and self.x_person <= 530:  # d => 7
                    self.x_person += 1  # right
                    not_moved = False

            key_index += 1

        if not_moved:
            if player.seconds == 1000:
                player.health = str(int(player.health) - 15)
                player.seconds = 0
            else:
                player.seconds += 1
        else:
            player.seconds = 0

        self.position_string = str(self.x_person) + " " + str(self.y_person)


def print_player(my):
    # message = player position, cursor position, shoot/don't, health, color
    return my.position_string + "*" + my.cursor + "*" + str(my.shoot) + "*" + str(my.health) + "*" + str(my.color) + "*"


def set_cursor_image(number):
    if number == "1":
        return pygame.image.load(r'.\images\orange_cursor.jpg')
    if number == "2":
        return pygame.image.load(r'.\images\red_cursor.jpg')
    if number == "3":
        return pygame.image.load(r'.\images\green_cursor.jpg')
    if number == "4":
        return pygame.image.load(r'.\images\blue_cursor.jpg')


def check_on_music():
    if not pygame.mixer.music.get_busy():  # just playing music for now
        pygame.mixer.init()
        pygame.mixer.music.load('music.mp3')
        pygame.mixer.music.play()


def sync_bombs(bombs_list):
    for bomb_location in bombs_list:
        if bomb_location != '':
            bomb_location = bomb_location.split("*")[0]
            screen.blit(bomb_image, (int(bomb_location.split()[0]), int(bomb_location.split()[-1])))


def sync_locations(locations, colors, names_list, healths):  # sync all locations
    color_index = 0
    font = pygame.font.SysFont('Comic Sans MS', 20)
    for color in colors:
        location = locations[color_index]
        hp = healths[color_index]
        if location != '' and hp != '':  # *the last value in the list is empty - need to fix!
            x_value = int(location.split()[0])
            y_value = int(location.split()[-1])
            img = player_switcher.get(str(color))
            img.set_colorkey(WHITE)
            person_name = names_list[color_index]
            text = font.render(person_name, False, (0, 0, 0))
            screen.blit(text, (x_value + 20, y_value))
            screen.blit(set_life(int(hp)), (x_value + 60, y_value))
            screen.blit(img, (x_value, y_value))

        color_index += 1


def set_life(hp):
    if hp == 90 or hp == 75:
        return full_bar
    if hp == 60 or hp == 45:
        return half_bar
    if hp == 30 or hp == 15 or hp == 0:
        return third_bar


# Constants
WHITE = (255, 255, 255)
size = (600, 600)

name = input("Enter your name: ")

player = Player(name)
# Server stuff
my_socket = socket.socket()
my_socket.connect(("127.0.0.1", 5555))
color_number = my_socket.recv(1024).decode()  # receive the player's color
player.color = color_number
my_socket.send(name.encode())

if color_number == "exit":
    pygame.quit()
    my_socket.close()
    exit()

player_switcher = {
    "1": pygame.image.load(r'.\images\orange_person.jpg'),
    "2": pygame.image.load(r'.\images\red_person.jpg'),
    "3": pygame.image.load(r'.\images\green_person.jpg'),
    "4": pygame.image.load(r'.\images\blue_person.jpg'),
}


# First reload
person_image = player_switcher.get(color_number)
person_image.set_colorkey(WHITE)

cursor_image = set_cursor_image(color_number)
cursor_image.set_colorkey(WHITE)

full_bar = pygame.image.load(r'.\images\full_bar.jpg')  # CREATE PHOTO
full_bar.set_colorkey(WHITE)
half_bar = pygame.image.load(r'.\images\half_bar.jpg')  # CREATE PHOTO
half_bar.set_colorkey(WHITE)
third_bar = pygame.image.load(r'.\images\third_bar.jpg')  # CREATE PHOTO
third_bar.set_colorkey(WHITE)
bomb_image = pygame.image.load(r'.\images\bomb2.png')
bomb_image.set_colorkey(WHITE)
clock = pygame.time.Clock()


pygame.init()
pygame.font.init()

pygame.mouse.set_visible(False)
screen = pygame.display.set_mode(size)
screen.fill(WHITE)
pygame.display.set_caption(name)
screen.blit(person_image, (player.x_person, player.y_person))
pygame.display.flip()


# Main loop
running = True
data = ""
my_font = pygame.font.SysFont('Comic Sans MS', 30)

while running:
    try:
        player.shoot = False
        screen.fill(WHITE)
        # check_on_music()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if player gets out
                running = False
                my_socket.send(("exit*" + color_number + "*" + name).encode())
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1=left
                player.shoot = True

        player.x_person = int(player.position_string.split()[0])
        player.y_person = int(player.position_string.split()[-1])

        player.check_change_in_position()

        # returns string of current player position after changes
        player.check_mouse_position()
        player.ammo_stuff()

        print(print_player(player))

        my_socket.send(print_player(player).encode())
        # message = player position, cursor position, shoot/don't, health, color

        r_list, w_list, x_list = select.select([my_socket], [], [], 1)
        for sock in r_list:
            data = sock.recv(1024).decode()
            if data == "win":
                running = False
            else:
                data = data.split("&")
                data.remove(data[0])

        print(data)
        # data =
        # [life list, positions, player numbers, names, bombs, specific player life, updated position]

        if data != [''] and data != "" and running:  # to prevent crashes
            player.health = data[5]
            if player.health == "0":
                running = False

            colors_list = data[2].split("*")
            all_health = data[0]
            all_health = all_health.split("*")  # each health separate by *

            # sends your person and cursor location to the server
            all_locations = data[1]  # string includes all the locations of players
            all_locations = all_locations.split("*")  # each location separate by *

            names = data[3]
            names = names.split("*")

            bombs = data[4]
            print(bombs)
            if bombs != "no bombs":
                bombs = bombs.split("*")
                sync_bombs(bombs)

            player.position_string = data[6]

            sync_locations(all_locations, colors_list, names, all_health)  # sync all locations
            courser_x, courser_y = int(player.cursor.split()[0]), int(player.cursor.split()[-1])
            screen.blit(cursor_image, (courser_x, courser_y))  # print your own coarser

            if player.seconds > 500:
                text_surface = my_font.render("Move!", False, (0, 0, 0))
                screen.blit(text_surface, (0, 560))

            text_surface = my_font.render(("Ammo: "+str(player.ammo)), False, (0, 0, 0))
            screen.blit(text_surface, (450, 0))

            pygame.display.flip()

    except():
        running = False

my_socket.send(("exit*" + color_number + "*" + name).encode())

if data == "win":
    text_surface = my_font.render((name+"! You Won!"), False, (0, 0, 0))
    screen.blit(text_surface, (220, 250))
    pygame.display.flip()
    pygame.time.wait(5000)  # 5 seconds - 5000 mls

pygame.quit()
my_socket.close()
