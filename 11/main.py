import pure_robot


class Monad:

    def __init__(self, func):
        self._func = func

    def bind(self, func):
        def new_func(state):
            result, next_state = self._func(state)
            next_func = func(result)
            return next_func(next_state)

        return Monad(new_func)

    def __call__(self, state):
        return self._func(state)


class RobotApi:

    def __init__(self, fn, transfer):
        self._f_transfer = transfer
        self._fn = fn
        self._cleaner_state = pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER)

    def setup(self, fn, transfer):
        self._f_transfer = transfer
        self._fn = fn

    def _to_monad(self, command):
        cmd = command.split(" ")
        fun = self._fn(cmd)

        def new_func(state):
            if cmd[0] == "move":
                return None, fun(self._f_transfer, int(cmd[1]), state)
            elif cmd[0] == "turn":
                return None, fun(self._f_transfer, int(cmd[1]), state)
            elif cmd[0] == "set":
                return None, fun(self._f_transfer, cmd[1], state)
            elif cmd[0] == "start":
                return None, fun(self._f_transfer, state)
            elif cmd[0] == "stop":
                return None, fun(self._f_transfer, state)

            return None, state

        return Monad(new_func)

    def __call__(self, commands):
        monads = [self._to_monad(command) for command in commands]
        program = Monad(lambda s: (None, s))
        for monad in monads:
            program = program.bind(lambda _, monad=monad: monad)

        _, final_state = program(self._cleaner_state)
        self._cleaner_state = final_state
        return self._cleaner_state


def robotFn(cmd):
    if cmd[0] == "move":
        return pure_robot.move
    elif cmd[0] == "turn":
        return pure_robot.turn
    elif cmd[0] == "set":
        return pure_robot.set_state
    elif cmd[0] == "start":
        return pure_robot.start
    elif cmd[0] == "stop":
        return pure_robot.stop
    return None


api = RobotApi(robotFn, pure_robot.transfer_to_cleaner)

if __name__ == "__main__":
    commands = ["move 100", "turn -90", "set soap", "start", "move 50", "stop"]
    result = api(commands)

    commands = ["move 100", "turn -90", "set soap", "start", "move 50", "stop"]
    result = api(commands)
