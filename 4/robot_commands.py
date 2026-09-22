from abc import ABC, abstractmethod
from typing import Any

from robot import RobotCleanerATD


class CommandATD(ABC):

    @abstractmethod
    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        pass

    @abstractmethod
    def get_execute_result(self) -> Any:
        pass


class MoveCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.move(int(args[0]))
        robot.transfer_message(f"POS {robot.get_x()}, {robot.get_y()}")

    def get_execute_result(self) -> Any:
        return self._result


class TurnCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.turn(int(args[0]))
        robot.transfer_message(f"ANGLE {robot.get_angle()}")

    def get_execute_result(self) -> Any:
        return self._result


class SetCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.set(args[0])
        robot.transfer_message(f"STATE {robot.get_selected_device()}")

    def get_execute_result(self) -> Any:
        return self._result


class StartCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.start()
        robot.transfer_message(f"START WITH {robot.get_selected_device()}")

    def get_execute_result(self) -> Any:
        return self._result


class StopCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.stop()
        robot.transfer_message("STOP")

    def get_execute_result(self) -> Any:
        return self._result
