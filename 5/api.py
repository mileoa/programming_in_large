from pure_robot import (
    turn,
    make,
    move,
    set_state,
    start,
    stop,
    RobotState,
    WATER,
    transfer_to_cleaner,
)


class RobotApi:

    def __init__(self, transfer):
        self._state = RobotState(0.0, 0.0, 0, WATER)
        self._transfer = transfer

    def turn(self, angle: int) -> None:
        self._state = turn(self._transfer, angle, self._state)

    def move(self, dist: int) -> None:
        self._state = move(self._transfer, dist, self._state)

    def set_state(self, new_state: int) -> None:
        self._state = set_state(self._transfer, new_state, self._state)

    def start(self) -> None:
        self._state = start(self._transfer, self._state)

    def stop(self) -> None:
        self._state = stop(self._transfer, self._state)

    def make(self, code: list[str]) -> None:
        self._state = make(self._transfer, code, self._state)


if __name__ == "__main__":
    robot = RobotApi(transfer_to_cleaner)
    code = ["move 100", "turn -90", "set soap", "start", "move 50", "stop"]
    robot.make(code)
