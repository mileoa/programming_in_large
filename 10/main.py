import pure_robot


class RobotApi:

    def setup(self, fn, transfer):
        self.f_transfer = transfer
        self.fn = fn
        self.commands = ["move", "turn", "set", "start", "stop"]

    def make(self, command):
        if not hasattr(self, "cleaner_state"):
            self.cleaner_state = pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER)

        command_attrs = command.split(" ")
        variables = []
        cmd = ""
        for command_part in command_attrs:
            if command_part not in self.commands:
                variables.append(command_part)
                continue

            cmd = command_part
            fun = self.fn(cmd)
            if cmd == "move":
                self.cleaner_state = fun(
                    self.f_transfer, int(variables.pop()), self.cleaner_state
                )
                variables = []
            elif cmd == "turn":
                self.cleaner_state = fun(
                    self.f_transfer, int(variables.pop()), self.cleaner_state
                )
                variables = []
            elif cmd == "set":
                self.cleaner_state = fun(
                    self.f_transfer, variables.pop(), self.cleaner_state
                )
                variables = []
            elif cmd == "start":
                self.cleaner_state = fun(self.f_transfer, self.cleaner_state)
                variables = []
            elif cmd == "stop":
                self.cleaner_state = fun(self.f_transfer, self.cleaner_state)
                variables = []
        return self.cleaner_state

    def __call__(self, command):
        return self.make(command)


def transfer_to_cleaner(message):
    print(message)


def double_move(transfer, dist, state):
    return pure_robot.move(transfer, dist * 2, state)


def robotFn(cmd):
    if cmd == "move":
        return pure_robot.move
    elif cmd == "turn":
        return pure_robot.turn
    elif cmd == "set":
        return pure_robot.set_state
    elif cmd == "start":
        return pure_robot.start
    elif cmd == "stop":
        return pure_robot.stop
    return None


if __name__ == "__main__":

    # Server
    api = RobotApi()
    api.setup(robotFn, transfer_to_cleaner)

    # Client
    api("100 move -90 turn soap set start 50 move stop")
