from dataclasses import dataclass
from typing import List, Protocol, Any
from enum import Enum
import math


# Состояние робота
@dataclass
class RobotState:
    x: float
    y: float
    angle: float
    state: int


# Режимы работы
class CleaningMode(Enum):
    WATER = 1
    SOAP = 2
    BRUSH = 3


# Протокол для команд
class Command(Protocol):
    def execute(self, state: RobotState) -> RobotState:
        pass

    def log(self) -> str:
        pass


# Конкретные команды
@dataclass
class MoveCommand:
    distance: float

    def execute(self, state: RobotState) -> RobotState:
        angle_rads = state.angle * (math.pi / 180.0)
        return RobotState(
            x=state.x + self.distance * math.cos(angle_rads),
            y=state.y + self.distance * math.sin(angle_rads),
            angle=state.angle,
            state=state.state,
        )

    def log(self) -> str:
        return f"MOVE {self.distance}"


@dataclass
class TurnCommand:
    angle: float

    def execute(self, state: RobotState) -> RobotState:
        return RobotState(
            x=state.x, y=state.y, angle=state.angle + self.angle, state=state.state
        )

    def log(self) -> str:
        return f"TURN {self.angle}"


@dataclass
class SetStateCommand:
    new_state: CleaningMode

    def execute(self, state: RobotState) -> RobotState:
        return RobotState(
            x=state.x, y=state.y, angle=state.angle, state=self.new_state.value
        )

    def log(self) -> str:
        return f"SET_STATE {self.new_state.name}"


@dataclass
class StartCommand:
    def execute(self, state: RobotState) -> RobotState:
        return state

    def log(self) -> str:
        return "START"


@dataclass
class StopCommand:
    def execute(self, state: RobotState) -> RobotState:
        return state

    def log(self) -> str:
        return "STOP"


@dataclass
class DummyCommand:
    def execute(self, state: RobotState) -> RobotState:
        return state

    def log(self) -> str:
        return "nothing heppend"


# Исполнитель команд
class CommandExecutor:
    def __init__(self):
        self.commands: List[Command] = []
        self._event_store = []

    def add_command(self, command: Command):
        self.commands.append(command)

    def execute_all(self, initial_state: RobotState) -> tuple[RobotState, List[str]]:
        current_state = initial_state
        self._event_store.append((DummyCommand(), initial_state))
        logs = []

        for cmd in self.commands:
            logs.append(cmd.log())
            current_state = cmd.execute(current_state)
            self._event_store.append((cmd, current_state))

        return current_state, logs

    def undo(self) -> RobotState:
        logs = []
        if len(self._event_store) == 0:
            logs.append("No events to undo")
            return RobotState(0.0, 0.0, 0, CleaningMode.WATER.value), logs

        cmd, current_state = self._event_store.pop()
        reversed_commands = []
        if isinstance(cmd, StartCommand):
            reversed_commands.append(StopCommand())
        if isinstance(cmd, StopCommand):
            reversed_commands.append(StartCommand())
        if isinstance(cmd, SetStateCommand):
            previous_internal_state = CleaningMode(self._event_store[-1][1].state)
            reversed_commands.append(SetStateCommand(previous_internal_state))
        if isinstance(cmd, TurnCommand):
            reversed_commands.append(TurnCommand(-cmd.angle))
        if isinstance(cmd, MoveCommand):
            reversed_commands.append(TurnCommand(180))
            reversed_commands.append(MoveCommand(cmd.distance))
            reversed_commands.append(TurnCommand(-180))
        if len(reversed_commands) == 0:
            reversed_commands.append(DummyCommand())

        reversed_state = current_state
        for reversed_cmd in reversed_commands:
            reversed_state = reversed_cmd.execute(reversed_state)
            logs.append(reversed_cmd.log())

        return reversed_state, logs


# Пример использования
def main():
    # Создаем исполнителя
    executor = CommandExecutor()

    # Добавляем команды
    executor.add_command(MoveCommand(100))
    executor.add_command(TurnCommand(-90))
    executor.add_command(SetStateCommand(CleaningMode.SOAP))
    executor.add_command(StartCommand())
    executor.add_command(MoveCommand(50))
    executor.add_command(StopCommand())

    # Выполняем все команды
    initial_state = RobotState(0.0, 0.0, 0, CleaningMode.WATER.value)
    final_state, final_logs = executor.execute_all(initial_state)
    print("Final state:", final_state)
    print("Command log:", final_logs)
    for i in range(7):
        reversed_state, logs = executor.undo()
        print("Reversed state:", reversed_state)
        print("Command log:", logs)


if __name__ == "__main__":
    main()
