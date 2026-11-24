from dataclasses import dataclass
from typing import List, Protocol, Any
from enum import Enum
import math
from abc import ABC


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


# Ответы
class Response(ABC):
    pass


class MoveResponseStatus:
    OK = "MOVE_OK"
    BARRIER = "HIT_BARRIER"


class StateResponseStatus:
    OK = "STATE_OK"
    NO_WATER = "OUT_OF_WATER"
    NO_SOAP = "OUT_OF_SOAP"


class TurnResponseStatus:
    OK = "TURN_OK"


@dataclass
class MoveResponse(Response):
    dist_x: float
    dist_y: float
    status: MoveResponseStatus


@dataclass
class TurnResponse(Response):
    angle: float
    status: TurnResponseStatus


@dataclass
class StateResponse(Response):
    new_state: CleaningMode
    status: StateResponseStatus


# Протокол для команд
class Command(Protocol):
    next_success_command: callable = lambda x: x
    next_fail_command: callable = lambda x: x

    def next(self, old_robot_state, response: Response) -> "Command":
        pass

    def interpret(self, robot_state: RobotState) -> Response:
        pass


# Конкретные команды
@dataclass
class MoveCommand(Command):
    dist: float

    def next(
        self, old_robot_state: RobotState, response: MoveResponse
    ) -> tuple[Command, RobotState]:
        if response.status != MoveResponseStatus.OK:
            return (self.next_fail_command, old_robot_state)
        new_robot_state = RobotState(
            response.dist_x,
            response.dist_y,
            old_robot_state.angle,
            old_robot_state.state,
        )
        return (self.next_success_command, new_robot_state)

    def interpret(self, robot_state: RobotState) -> MoveResponse:
        angle_rads = robot_state.angle * (math.pi / 180.0)
        dist_x = robot_state.x + self.dist * math.cos(angle_rads)
        dist_y = robot_state.y * math.sin(angle_rads)

        constrained_x, constrained_y, move_result = self._check_position(dist_x, dist_y)
        print(f"MOVE {self.dist}")
        return MoveResponse(
            constrained_x,
            constrained_y,
            move_result,
        )

    def _check_position(self, x: float, y: float) -> tuple[float, float, str]:
        constrained_x = max(0, min(100, x))
        constrained_y = max(0, min(100, y))

        if x == constrained_x and y == constrained_y:
            return (x, y, MoveResponseStatus.OK)
        return MoveResponse(constrained_x, constrained_y, MoveResponseStatus.BARRIER)


@dataclass
class TurnCommand(Command):
    angle: float

    def next(
        self, old_robot_state: RobotState, response: TurnResponse
    ) -> tuple[Command, RobotState]:
        if response.status == TurnResponseStatus.OK:
            new_robot_state = RobotState(
                old_robot_state.x,
                old_robot_state.y,
                response.angle,
                old_robot_state.state,
            )
            return (self.next_success_command, new_robot_state)
        return (self.next_fail_command, old_robot_state)

    def interpret(self, robot_state: RobotState) -> TurnResponse:
        new_angle = robot_state.angle + self.angle
        turn_result = TurnResponseStatus.OK
        print(f"ANGLE {self.angle}")
        return TurnResponse(
            new_angle,
            turn_result,
        )


@dataclass
class SetStateCommand(Command):
    new_state: CleaningMode

    def next(self, old_robot_state: RobotState, response: StateResponse) -> Command:
        if response.status == StateResponseStatus.OK:
            new_robot_state = RobotState(
                old_robot_state.x,
                old_robot_state.y,
                old_robot_state.angle,
                response.new_state,
            )
            return (self.next_success_command, new_robot_state)
        return (self.next_fail_command, old_robot_state)

    def interpret(self, robot_state: RobotState) -> StateResponse:
        print(f"SET_STATE {self.new_state}")
        return StateResponse(self.new_state, self._check_resources(self.new_state))

    def _check_resources(self, new_mode: int) -> StateResponseStatus:
        if new_mode == CleaningMode.WATER:
            # ....
            return StateResponseStatus.NO_WATER
        elif new_mode == CleaningMode.SOAP:
            # ....
            return StateResponseStatus.NO_SOAP
        return StateResponseStatus.OK


@dataclass
class StopCommand(Command):
    def next(self, old_robot_state: RobotState, response: None) -> None:
        pass

    def interpret(self, robot_state: RobotState) -> None:
        print("STOP")
        return None


# AST
class AST:

    def __init__(self):
        self.head = StopCommand()
        self.tail = self.head

    def add_node(self, command):
        command.next_success_command = self.head
        command.next_fail_command = self.tail
        self.head = command

    def interpret(self, robot_state: RobotState) -> RobotState:
        new_robot_state = robot_state
        current_node = self.head
        response = current_node.interpret(robot_state)
        while response is not None:
            current_node, new_robot_state = current_node.next(new_robot_state, response)
            response = current_node.interpret(new_robot_state)

        return new_robot_state


# Пример использования
def main():
    # Создаем исполнителя
    executor = AST()

    # Добавляем команды
    executor.add_node(MoveCommand(50))
    executor.add_node(SetStateCommand(CleaningMode.SOAP))
    executor.add_node(TurnCommand(-90))
    executor.add_node(MoveCommand(100))

    # Выполняем все команды
    initial_state = RobotState(0.0, 0.0, 0, CleaningMode.WATER.value)
    final_state = executor.interpret(initial_state)

    # Выводим результаты
    print("Final state:", final_state)


if __name__ == "__main__":
    main()
