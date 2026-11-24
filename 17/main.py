from dataclasses import dataclass, replace
from typing import Callable
import pure_robot


@dataclass
class RobotState:
    x: float
    y: float
    angle: float
    state: int

    move: Callable[[float], "RobotState":]
    turn: Callable[[float], "RobotState"]
    set_state: Callable[[int], "RobotState"]
    start: Callable[[], "RobotState"]
    stop: Callable[[], "RobotState"]
    transfer: Callable[[str], None]

    def __post_init__(self):
        raw_move = self.move
        raw_turn = self.turn
        raw_set_state = self.set_state
        raw_start = self.start
        raw_stop = self.stop

        def wrap(new_raw_state) -> "RobotState":
            return replace(
                self,
                x=new_raw_state.x,
                y=new_raw_state.y,
                angle=new_raw_state.angle,
                state=new_raw_state.state,
                move=raw_move,
                turn=raw_turn,
                set_state=raw_set_state,
                start=raw_start,
                stop=raw_stop,
            )

        self.move = lambda dist: wrap(raw_move(self.transfer, dist, self))
        self.turn = lambda angle: wrap(raw_turn(self.transfer, angle, self))
        self.set_state = lambda new_state: wrap(
            raw_set_state(self.transfer, new_state, self)
        )
        self.start = lambda: wrap(raw_start(self.transfer, self))
        self.stop = lambda: wrap(raw_stop(self.transfer, self))


def main():

    # Если переписать pure_robot под аналог AST, где AST это и сам робот, то можно сделать более удобное ветвление и циклы.
    robot = RobotState(
        0,
        0,
        0,
        pure_robot.WATER,
        pure_robot.move,
        pure_robot.turn,
        pure_robot.set_state,
        pure_robot.start,
        pure_robot.stop,
        pure_robot.transfer_to_cleaner,
    )

    print(robot.move(100).turn(-90).set_state(pure_robot.SOAP).start().move(50).stop())


if __name__ == "__main__":
    main()
