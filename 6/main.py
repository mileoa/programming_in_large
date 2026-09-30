import pure_robot
from typing import Iterable


def main(
    robot_state: pure_robot.RobotState, code: Iterable[str]
) -> pure_robot.RobotState:
    return pure_robot.make(pure_robot.transfer_to_cleaner, code, robot_state)


if __name__ == "__main__":
    robot_state = pure_robot.RobotState(0, 0, 0, pure_robot.WATER)
    code = ("move 100", "turn -90", "set soap", "start", "move 50", "stop")
    new_state = main(robot_state, code)
    print(new_state.x)
    print(new_state.y)
    print(new_state.angle)
    print(new_state.state)
