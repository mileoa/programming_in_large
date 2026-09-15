from abc import ABC, abstractmethod
import math
from typing import Any, Callable


class RobotCleanerATD(ABC):

    @abstractmethod
    def move(self, meters: int) -> None:
        """
        Предусловие: количество метров для перемещения >= 0
        Постусловие: робот перемещен на указанное количество метров вперед
        """
        pass

    @abstractmethod
    def turn(self, angle: int) -> None:
        """
        Постусловие: робот повернут на указанное количество градусов
        """
        pass

    @abstractmethod
    def set(self, device: str) -> None:
        """
        Предусловие: устройство находится в арсенале робота
        Постусловие: робот выбрал указанное устройство
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Предусловие: робот выбрал устройство
        Постусловие: включено выбранное роботом устройство
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Предусловие: робот выбрал устройство и устройство включено
        Постусловие: выбранное роботом устройство выключено
        """
        pass

    @abstractmethod
    def set_x(self, x: int) -> None:
        """
        Постусловие: координата x установлена
        """
        pass

    @abstractmethod
    def set_y(self, y: int) -> None:
        """
        Постусловие: координата y установлена
        """
        pass

    @abstractmethod
    def set_angle(self, angle: int) -> None:
        """
        Постусловие: робот повернут в указанный угол
        """
        pass

    @abstractmethod
    def get_x(self) -> int:
        pass

    @abstractmethod
    def get_y(self) -> int:
        pass

    @abstractmethod
    def get_angle(self) -> int:
        pass

    @abstractmethod
    def get_selected_device(self) -> str:
        """
        Получить выбранное роботом устройство
        """
        pass

    @abstractmethod
    def get_available_devices(self) -> list[str]:
        """
        Получить устройства доступные для использования
        """
        pass

    @abstractmethod
    def get_device_state(self) -> bool:
        """
        Получить статус работы устройства.
        """
        pass


class RobotCleaner(RobotCleanerATD):
    def __init__(self) -> None:
        super().__init__()
        self._x: int = 0
        self._y: int = 0
        self._angle: int = 0
        self._available_devices: list[str] = ["soap", "water", "brush"]
        self._is_device_on: bool = False
        self._selected_device: str = "water"

    def move(self, meters: int) -> None:
        if meters < 0:
            raise ValueError("Количество метров не может быть отрицательным")
        angle_radians = math.radians(self._angle)
        self._x += int(math.cos(angle_radians) * meters)
        self._y += int(math.sin(angle_radians) * meters)

    def turn(self, angle: int) -> None:
        self._angle = (self._angle + angle) % 360

    def set(self, device: str) -> None:
        if device not in self._available_devices:
            raise ValueError(f"Устройство {device} недоступно для выбора")
        self._selected_device = device

    def start(self) -> None:
        if self._selected_device == "":
            raise ValueError("Устройство не было выбрано")
        self._is_device_on = True

    def stop(self) -> None:
        if self._selected_device == "":
            raise ValueError("Устройство не было выбрано")
        if not self._is_device_on:
            raise ValueError("Устройство не было включено")
        self._is_device_on = False

    def set_x(self, x: int) -> None:
        self._x = x

    def set_y(self, y: int) -> None:
        self._y = y

    def set_angle(self, angle: int) -> None:
        self._angle = angle % 360

    def get_x(self) -> int:
        return self._x

    def get_y(self) -> int:
        return self._y

    def get_angle(self) -> int:
        return self._angle

    def get_selected_device(self) -> str:
        return self._selected_device

    def get_available_devices(self) -> list[str]:
        return self._available_devices

    def get_device_state(self) -> bool:
        return self._is_device_on


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
        print("POS", f"{robot.get_x()}, {robot.get_y()}")

    def get_execute_result(self) -> Any:
        return self._result


class TurnCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.turn(int(args[0]))
        print("ANGLE", robot.get_angle())

    def get_execute_result(self) -> Any:
        return self._result


class SetCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.set(args[0])
        print("STATE", robot.get_selected_device())

    def get_execute_result(self) -> Any:
        return self._result


class StartCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.start()
        print("START WITH", robot.get_selected_device())

    def get_execute_result(self) -> Any:
        return self._result


class StopCommand(CommandATD):

    def __init__(self) -> None:
        self._result: Any = None

    def execute(self, robot: RobotCleanerATD, *args: str) -> None:
        self._result = robot.stop()
        print("STOP")

    def get_execute_result(self) -> Any:
        return self._result


def main() -> None:
    function_by_command: dict[str, CommandATD] = {
        "move": MoveCommand(),
        "turn": TurnCommand(),
        "set": SetCommand(),
        "start": StartCommand(),
        "stop": StopCommand(),
    }
    commands = ["move 100", "turn -90", "set soap", "start", "move 50", "stop"]

    robot: RobotCleanerATD = RobotCleaner()
    for command in commands:
        parametrs: list[str] = command.split(" ")
        command_name, args = parametrs[0], parametrs[1:]
        command_function: CommandATD = function_by_command[command_name]
        command_function.execute(robot, *args)


if __name__ == "__main__":
    main()
