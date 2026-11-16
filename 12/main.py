from abc import ABC, abstractmethod
from functools import reduce
import pure_robot


class Command(ABC):

    @abstractmethod
    def execute(self, transfer, state, *args):
        pass


class MoveCommand(Command):

    def execute(self, transfer, state, *args) -> None:
        return pure_robot.move(transfer, *args, state)


class TurnCommand(Command):

    def execute(self, transfer, state, *args) -> None:
        return pure_robot.turn(transfer, *args, state)


class SetStateCommand(Command):

    def execute(self, transfer, state, *args) -> None:
        return pure_robot.set_state(transfer, *args, state)


class StartCommand(Command):

    def execute(self, transfer, state, *args) -> None:
        return pure_robot.start(transfer, state)


class StopCommand(Command):

    def execute(self, transfer, state, *args) -> None:
        return pure_robot.stop(transfer, state)


if __name__ == "__main__":
    transfer = pure_robot.transfer_to_cleaner
    commands = [
        lambda state: pure_robot.move(transfer, 100, state),
        lambda state: pure_robot.turn(transfer, -90, state),
        lambda state: pure_robot.set_state(transfer, pure_robot.SOAP, state),
        lambda state: pure_robot.start(transfer, state),
        lambda state: pure_robot.move(transfer, 50, state),
        lambda state: pure_robot.stop(transfer, state),
    ]

    new_state = reduce(
        lambda current_state, cmd: cmd(current_state),
        commands,
        pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER),
    )
