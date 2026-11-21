from functools import wraps
from collections import namedtuple
import math

RobotState = namedtuple("RobotState", "x y angle state water_amount soap_amount")


WATER = 1
SOAP = 2
BRUSH = 3


class MoveResponse:
    OK = "MOVE_OK"
    BARRIER = "HIT_BARRIER"


class SetStateResponse:
    OK = "STATE_OK"
    NO_WATER = "OUT_OF_WATER"
    NO_SOAP = "OUT_OF_SOAP"


class StateMonad:
    def __init__(self, state, log=None):
        self.state = state
        self.log = log or []

    def bind(self, func):
        new_state, new_log = func(self.state, self.log)
        return StateMonad(new_state, new_log)


def move(dist):
    def inner(old_state, log):
        angle_rads = old_state.angle * (math.pi / 180.0)
        new_state = RobotState(
            old_state.x + dist * math.cos(angle_rads),
            old_state.y + dist * math.sin(angle_rads),
            old_state.angle,
            old_state.state,
            old_state.water_amount,
            old_state.soap_amount,
        )
        constrained_x, constrained_y, check_result = check_position(
            new_state.x, new_state.y
        )
        if check_result != MoveResponse.OK:
            new_state = RobotState(
                constrained_x,
                constrained_y,
                old_state.angle,
                old_state.state,
                old_state.water_amount,
                old_state.soap_amount,
            )
            return old_state, log + [
                f"{check_result} ({constrained_x},{constrained_y})",
                f"POS({int(new_state.x)},{int(new_state.y)})",
            ]
        return new_state, log + [f"POS({int(new_state.x)},{int(new_state.y)})"]

    return inner


def turn(angle):
    def inner(old_state, log):
        new_state = RobotState(
            old_state.x,
            old_state.y,
            old_state.angle + angle,
            old_state.state,
            old_state.water_amount,
            old_state.soap_amount,
        )
        return new_state, log + [f"ANGLE {new_state.angle}"]

    return inner


def set_state(new_mode):
    def inner(old_state, log):
        if new_mode == WATER:
            new_state = RobotState(
                old_state.x,
                old_state.y,
                old_state.angle,
                new_mode,
                old_state.water_amount - 1,
                old_state.soap_amount,
            )
        if new_mode == SOAP:
            new_state = RobotState(
                old_state.x,
                old_state.y,
                old_state.angle,
                new_mode,
                old_state.water_amount,
                old_state.soap_amount - 1,
            )
        else:
            new_state = RobotState(
                old_state.x,
                old_state.y,
                old_state.angle,
                new_mode,
                old_state.water_amount,
                old_state.soap_amount,
            )
        check_result = check_resources(new_state, new_mode)
        if check_result != SetStateResponse.OK:
            return old_state, log + [check_result]
        return new_state, log + [f"STATE {new_mode}"]

    return inner


def start(old_state, log):
    return old_state, log + ["START"]


def stop(old_state, log):
    return old_state, log + ["STOP"]


def check_position(x: float, y: float) -> tuple[float, float, str]:
    constrained_x = max(0, min(100, x))
    constrained_y = max(0, min(100, y))

    if x == constrained_x and y == constrained_y:
        return (x, y, MoveResponse.OK)
    return (constrained_x, constrained_y, MoveResponse.BARRIER)


def check_resources(state: RobotState, new_mode: int) -> SetStateResponse:
    if new_mode == WATER and state.water_amount < 0:
        return SetStateResponse.NO_WATER
    if new_mode == SOAP and state.soap_amount < 0:
        return SetStateResponse.NO_SOAP
    return SetStateResponse.OK


if __name__ == "__main__":
    initial_state = StateMonad(RobotState(0.0, 0.0, 0, WATER, 3, 0))
    result = (
        initial_state.bind(move(100))
        .bind(turn(-90))
        .bind(set_state(SOAP))
        .bind(start)
        .bind(move(50))
        .bind(stop)
    )

    print(f"Final state: {result.state}")
    print(f"Log: {result.log}")
