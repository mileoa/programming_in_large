import pure_robot


class RobotApi:

    def __init__(self, f_transfer):
        self.f_transfer = f_transfer

    def make(self, command, function_robot):
        if not hasattr(self, "cleaner_state"):
            self.cleaner_state = pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER)

        cmd = command.split(" ")
        if cmd[0] == "move":
            self.cleaner_state = function_robot(
                self.f_transfer, int(cmd[1]), self.cleaner_state
            )
        elif cmd[0] == "turn":
            self.cleaner_state = function_robot(
                self.f_transfer, int(cmd[1]), self.cleaner_state
            )
        elif cmd[0] == "set":
            self.cleaner_state = function_robot(
                self.f_transfer, cmd[1], self.cleaner_state
            )
        elif cmd[0] == "start":
            self.cleaner_state = function_robot(self.f_transfer, self.cleaner_state)
        elif cmd[0] == "stop":
            self.cleaner_state = function_robot(self.f_transfer, self.cleaner_state)
        return self.cleaner_state

    def __call__(self, command, function_robot):
        return self.make(command, function_robot)


def transfer_to_cleaner(message):
    print(message)


def double_move(transfer, dist, state):
    return pure_robot.move(transfer, dist * 2, state)


if __name__ == "__main__":
    # Server
    api = RobotApi(pure_robot.transfer_to_cleaner)

    # Cliient
    api("move 100", pure_robot.move)
    api("turn -90", pure_robot.turn)
    api("set soap", pure_robot.set_state)
    api("start", pure_robot.start)
    api("move 50", pure_robot.move)
    s = api("stop", pure_robot.stop)
