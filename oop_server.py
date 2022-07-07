import socket
import select
import pygame


def send_person_locations(all_locations):  # send locations of all players to all players
    all_person_locations = ""
    for location in all_locations:
        all_person_locations += location + "*"

    return all_person_locations


def send_bombs(bombs):
    all_bombs_locations = ""
    for bombs_location in range(0, len(bombs), 2):
        all_bombs_locations += bombs[bombs_location] + "*"

    if all_bombs_locations == "":
        return "no bombs"

    return all_bombs_locations


def send_cursor_locations(cursors):  # send locations of all cursors to all players
    all_cursors_locations = ""
    for cursor in cursors:
        all_cursors_locations += cursor + "*"

    return all_cursors_locations


def send_colors(colors):
    colors_string = ""
    for color in colors:
        colors_string += color + "*"
    return colors_string


def send_health_bars(health_bars):
    health_bars_string = ""
    for health in health_bars:
        health_bars_string += health + "*"

    return health_bars_string


def bomb_location_legal(player_locations, bombs):
    for bomb in range(0, len(bombs), 2):
        if bombs[bomb+1] == 1000:
            bomb_x = int(bombs[bomb].split()[0])
            bomb_y = int(bombs[bomb].split()[-1])
            not_deleted = True
            for player in player_locations:
                if not_deleted:
                    player_x = int(player.split()[0])
                    player_y = int(player.split()[-1])
                    if player_x - 50 <= bomb_x <= player_x + 50 and player_y - 50 <= bomb_y <= player_y + 100\
                            or 0 <= bomb_x <= 50 and 0 <= bomb_y <= 50:
                        bombs.remove(bombs[bomb])
                        bombs.remove(bombs[bomb])
                        not_deleted = False

    return bombs


def delete_bombs(bombs_list):
    removed_number = 0
    for bomb_life_index in range(1, len(bombs_list), 2):
        life = bombs_list[bomb_life_index-removed_number] - 1
        if life == 0:
            place = bombs_list[bomb_life_index-removed_number-1]
            time = bombs_list[bomb_life_index-removed_number]
            bombs_list.remove(place)
            bombs_list.remove(time)
            removed_number += 2
        else:
            bombs_list[bomb_life_index-removed_number] = life

    return bombs_list


def search_hit_player(locations, health_bars, bombs):
    player_index = 0
    for player_location in locations:
        player_x = int(player_location.split()[0])
        player_y = int(player_location.split()[-1])
        for bomb_location_index in range(0, len(bombs), 2):
            bomb_location_x = int(bombs[bomb_location_index].split()[0])
            bomb_location_y = int(bombs[bomb_location_index].split()[-1])
            if bomb_location_x-30 <= player_x <= bomb_location_x + 30 and\
                    bomb_location_y-30 <= player_y <= bomb_location_y+30:

                health_bars[player_index] = str(int(health_bars[player_index]) - 15)
                locations[player_index] = "0 0"

        player_index += 1

    return health_bars, locations


def send_names(name_list):
    names_string = ""
    for name in name_list:
        names_string += name + "*"

    return names_string


def sync(health_bar, person_locations, client_sockets, colors_list, name, bombs):
    message = "&" + send_health_bars(health_bar) + "&"  # locations of all healths to all players
    message += send_person_locations(person_locations) + "&"  # locations of all players to all players
    message += send_colors(colors_list) + "&"
    message += send_names(name) + "&"
    message += send_bombs(bombs) + "&"

    current_socket_index = 0
    for current_socket in client_sockets:
        current_socket.send((message + health_bar[current_socket_index] + "&" +
                             person_locations[current_socket_index] + "&").encode())
        current_socket_index += 1


def edit_player_list():
    players_list = []
    max_players = int(input("Enter max players"))
    color = 1
    player_count = 0
    while player_count < max_players:
        players_list.append(str(color))
        player_count += 1
        color += 1
        if color == 5:
            color = 1

    return players_list, max_players


def main():
    port = 5555
    ip = "0.0.0.0"
    print("Setting up server...")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(True)
    print("Listening for clients...")

    client_sockets = []
    person_locations = []
    cursor_locations = []
    health_bar = []
    colors = []
    names = []
    bombs = []
    players = 0
    start = False
    print(socket.gethostbyname(socket.gethostname()))

    pygame.init()
    pygame.display.set_mode((1, 1))
    pygame.display.set_caption("server")
    pygame.display.flip()

    players_left, max_players = edit_player_list()

    while not start:
        r_list, w_list, x_list = select.select([server_socket] + client_sockets, client_sockets, [], 1)
        for current_socket in r_list:
            if current_socket is server_socket:  # till 4 players max
                connection, client_address = current_socket.accept()
                if players == max_players:
                    connection.send("exit".encode())
                    connection.close()
                else:
                    print("New client joined!", client_address)
                    client_sockets.append(connection)
                    print(str(players_left[0]))
                    connection.send(str(players_left[0]).encode())
                    names.append(connection.recv(1024).decode())
                    players_left.remove(players_left[0])
                    players += 1

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and players > 1:
                start = True

    while len(client_sockets) != 1:
        clone_client_sockets = client_sockets.copy()
        for current_socket in clone_client_sockets:
            message = current_socket.recv(1024).decode().split("*")
            if message[0] == "exit":
                players -= 1
                client_sockets.remove(current_socket)
                names.remove(message[-1])
                current_socket.close()
                players_left.append(message[1])

            else:
                person_location = message[0]
                cursor_location = message[1]
                shoot_order = message[2]
                health = message[3]
                color_number = message[4]

                if shoot_order == "shoot":
                    bomb_location = str(int(cursor_location.split()[0])-30)  # bomb x
                    bomb_location += " " + str(int(cursor_location.split()[-1])-40)  # bomb y
                    bombs.append(bomb_location)
                    bombs.append(1000)

                person_locations.append(person_location)  # list of all person locations
                cursor_locations.append(cursor_location)  # list of all cursor locations
                health_bar.append(health)
                colors.append(color_number)

        bombs = bomb_location_legal(person_locations, bombs)
        bombs = delete_bombs(bombs)

        health_bar, person_locations = search_hit_player(person_locations, health_bar, bombs)
        sync(health_bar, person_locations, client_sockets, colors, names, bombs)

        health_bar = []   # reset the list
        person_locations = []  # reset the list
        cursor_locations = []  # reset the list
        colors = []  # reset the list

    client_sockets[0].recv(1024)
    client_sockets[0].send("win".encode())
    pygame.quit()


if __name__ == "__main__":
    main()
