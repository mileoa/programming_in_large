from robot_commands import (
    MoveCommand,
    SetCommand,
    StartCommand,
    StopCommand,
    TurnCommand,
    CommandATD,
)
from robot import RobotCleanerATD, RobotCleaner


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
