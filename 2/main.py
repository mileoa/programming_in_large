import math


def set_code():
    global code
    # входная программа управления роботом
    code = ("move 100", "turn -90", "set soap", "start", "move 50", "stop")


def set_default_variables():
    global WATER, SOAP, BRUSH, x, y, angle, state
    # режимы работы устройства очистки
    WATER = 1  # полив водой
    SOAP = 2  # полив мыльной пеной
    BRUSH = 3  # чистка метлой

    x = 0.0
    y = 0.0
    angle = 0
    state = WATER


def move(dist):
    global x, y
    angle_rads = angle * (math.pi / 180.0)
    x += dist * math.cos(angle_rads)
    y += dist * math.sin(angle_rads)
    print("POS(", x, ",", y, ")")


def turn(turn_angle):
    global angle
    angle += turn_angle
    print("ANGLE", angle)


def set_state(new_state):
    global state
    if new_state == "water":
        state = WATER
    elif new_state == "soap":
        state = SOAP
    elif new_state == "brush":
        state = BRUSH
    print("STATE", state)


def start():
    global state
    print("START WITH", state)


def stop():
    print("STOP")


def main():
    global code
    # главная программа
    for command in code:
        cmd = command.split(" ")
        if cmd[0] == "move":
            dist = int(cmd[1])
            move(dist)
        elif cmd[0] == "turn":
            turn_angle = int(cmd[1])
            turn(turn_angle)
        elif cmd[0] == "set":
            new_state = cmd[1]
            set_state(new_state)
        elif cmd[0] == "start":
            start()
        elif cmd[0] == "stop":
            stop()


if __name__ == "__main__":
    set_code()
    set_default_variables()
    main()
