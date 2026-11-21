from dataclasses import dataclass
from collections import defaultdict
from typing import List, Protocol, Optional, TypeVar
from enum import Enum
import math
from abc import ABC, abstractmethod

T = TypeVar("T", bound="RequestedEvent")


@dataclass
class RobotState:
    x: float
    y: float
    angle: float
    state: int


class CleaningMode(Enum):
    WATER = 1
    SOAP = 2
    BRUSH = 3


class Event(ABC):
    @abstractmethod
    def apply(self, state: RobotState) -> RobotState:
        pass

    @abstractmethod
    def get_event_type(self) -> str:
        pass


class RequestedEvent(Event):
    def apply(self, state) -> RobotState:
        return state

    @abstractmethod
    def get_event_type(self) -> str:
        pass


@dataclass
class MoveRequestedEvent(RequestedEvent):
    distance: float

    def get_event_type(self) -> str:
        return f"move request {self.distance}"


@dataclass
class TurnRequestedEvent(RequestedEvent):
    angle: float

    def get_event_type(self) -> str:
        return f"turn request {self.angle}"


@dataclass
class SetStateRequestedEvent(RequestedEvent):
    new_state: CleaningMode

    def get_event_type(self) -> str:
        return f"set state request {self.new_state.name}"


@dataclass
class StartRequestedEvent(RequestedEvent):
    @classmethod
    def get_event_type(cls) -> str:
        return "start_request"


@dataclass
class StopRequestedEvent(RequestedEvent):
    @classmethod
    def get_event_type(cls) -> str:
        return "stop_request"


@dataclass
class RobotMovedEvent(Event):
    distance: float

    def apply(self, state: RobotState) -> RobotState:
        angle_rads = state.angle * (math.pi / 180.0)
        return RobotState(
            x=state.x + self.distance * math.cos(angle_rads),
            y=state.y + self.distance * math.sin(angle_rads),
            angle=state.angle,
            state=state.state,
        )

    def get_event_type(self) -> str:
        return f"ROBOT_MOVED {self.distance}"


@dataclass
class RobotTurnedEvent(Event):
    angle: float

    def apply(self, state: RobotState) -> RobotState:
        return RobotState(
            x=state.x, y=state.y, angle=state.angle + self.angle, state=state.state
        )

    def get_event_type(self) -> str:
        return f"ROBOT_TURNED {self.angle}"


@dataclass
class RobotStateChangedEvent(Event):
    new_state: CleaningMode

    def apply(self, state: RobotState) -> RobotState:
        return RobotState(
            x=state.x, y=state.y, angle=state.angle, state=self.new_state.value
        )

    def get_event_type(self) -> str:
        return f"ROBOT_STATE_CHANGED {self.new_state.name}"


@dataclass
class RobotStartedEvent(Event):
    def apply(self, state: RobotState) -> RobotState:
        return state

    def get_event_type(self) -> str:
        return "ROBOT_STARTED"


@dataclass
class RobotStoppedEvent(Event):
    def apply(self, state: RobotState) -> RobotState:
        return state

    def get_event_type(self) -> str:
        return "ROBOT_STOPPED"


class Command(Protocol):
    def handle(self, current_state: RobotState) -> List[Event]:
        pass

    def get_command_type(self) -> str:
        pass


@dataclass
class MoveCommand:
    distance: float

    def handle(self) -> List[Event]:
        return [MoveRequestedEvent(self.distance)]

    def get_command_type(self) -> str:
        return f"MOVE {self.distance}"


@dataclass
class TurnCommand:
    angle: float

    def handle(self) -> List[Event]:
        return [TurnRequestedEvent(self.angle)]

    def get_command_type(self) -> str:
        return f"TURN {self.angle}"


@dataclass
class SetStateCommand:
    new_state: CleaningMode

    def handle(self) -> List[Event]:
        return [SetStateRequestedEvent(self.new_state)]

    def get_command_type(self) -> str:
        return f"SET_STATE {self.new_state.name}"


@dataclass
class StartCommand:
    def handle(self) -> List[Event]:
        return [StartRequestedEvent()]

    def get_command_type(self) -> str:
        return "START"


@dataclass
class StopCommand:
    def handle(self) -> List[Event]:
        return [StopRequestedEvent()]

    def get_command_type(self) -> str:
        return "STOP"


class EventProcessor(ABC):
    def __init__(self, event_store: "EventStore", projector: "StateProjector"):
        self._event_store = event_store
        self._projector = projector

    @abstractmethod
    def notify(self, robot_id: int, requested_event: RequestedEvent) -> RobotState:
        pass


class RovbotEventProcessor(EventProcessor):

    def notify(self, robot_id, requested_event: RequestedEvent) -> RobotState:

        if isinstance(requested_event, MoveRequestedEvent):
            self._event_store.append_events(
                robot_id, [RobotMovedEvent(requested_event.distance)]
            )
        elif isinstance(requested_event, TurnRequestedEvent):
            self._event_store.append_events(
                robot_id, [RobotTurnedEvent(requested_event.angle)]
            )
        elif isinstance(requested_event, SetStateRequestedEvent):
            self._event_store.append_events(
                robot_id, [RobotStateChangedEvent(requested_event.new_state)]
            )
        elif isinstance(requested_event, StopRequestedEvent):
            self._event_store.append_events(robot_id, [RobotStoppedEvent()])
        elif isinstance(requested_event, StartRequestedEvent):
            self._event_store.append_events(robot_id, [RobotStartedEvent()])


class EventStore:
    def __init__(self):
        self._events: dict[str, List[Event]] = defaultdict(list)
        self._subscribers: dict[str, List[EventProcessor]] = defaultdict(list)

    def append_events(self, robot_id: str, events: List[Event]) -> None:
        for event in events:
            self._events[robot_id].append(event)
            for subscriber in self._subscribers[type(event)]:
                subscriber.notify(robot_id, event)

    def get_events(self, robot_id: str) -> List[Event]:
        return self._events[robot_id]

    def get_events_from_version(self, robot_id: str, from_version: int) -> List[Event]:
        events = self.get_events(robot_id)
        return events[from_version:] if from_version < len(events) else []

    def subscribe(
        self, event_request: RequestedEvent, processor: EventProcessor
    ) -> None:
        self._subscribers[event_request].append(processor)


class StateProjector:
    def __init__(self, initial_state: RobotState):
        self._initial_state = initial_state

    def project_state(self, events: List[Event]) -> RobotState:
        current_state = self._initial_state
        for event in events:
            current_state = event.apply(current_state)
        return current_state


class CommandHandler:
    def __init__(self, event_store: EventStore, state_projector: StateProjector):
        self._event_store = event_store
        self._state_projector = state_projector

    def handle_command(self, robot_id: str, command: Command) -> None:
        new_event_requests = command.handle()
        if new_event_requests:
            self._event_store.append_events(robot_id, new_event_requests)
        new_state = self._state_projector.project_state(
            self._event_store.get_events(robot_id)
        )
        return new_state


def main():

    event_store = EventStore()
    initial_state = RobotState(0.0, 0.0, 0, CleaningMode.WATER.value)
    state_projector = StateProjector(initial_state)
    command_handler = CommandHandler(event_store, state_projector)

    processor = RovbotEventProcessor(event_store, state_projector)
    for req_type in (
        MoveRequestedEvent,
        TurnRequestedEvent,
        SetStateRequestedEvent,
        StartRequestedEvent,
        StopRequestedEvent,
    ):
        event_store.subscribe(req_type, processor)

    robot_id = "robot_001"

    commands = [
        MoveCommand(100),
        TurnCommand(-90),
        SetStateCommand(CleaningMode.SOAP),
        StartCommand(),
        MoveCommand(50),
        StopCommand(),
    ]

    for i, cmd in enumerate(commands):
        print(f"Cmd {i + 1}: {cmd.get_command_type()}")
        final_state = command_handler.handle_command(robot_id, cmd)
        print(f"State: {final_state}")
        print()


if __name__ == "__main__":
    main()
