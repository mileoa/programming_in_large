import pure_robot
from abc import ABC, abstractmethod


# класс Чистильщик API
class CleanerApiATD(ABC):

    @abstractmethod
    def __init__(self, cleaner, cleaner_state):
        pass

    @abstractmethod
    def transfer_to_cleaner(self, message):
        pass

    @abstractmethod
    def get_x(self):
        pass

    @abstractmethod
    def get_y(self):
        pass

    @abstractmethod
    def get_angle(self):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def activate_cleaner(self, code):
        pass


class CleanerApi(CleanerApiATD):

    def __init__(self, cleaner, cleaner_state):
        self._cleaner = cleaner
        self.cleaner_state = cleaner_state

    def transfer_to_cleaner(self, message):
        self._cleaner.transfer_to_cleaner(message)

    def get_x(self):
        return self.cleaner_state.x

    def get_y(self):
        return self.cleaner_state.y

    def get_angle(self):
        return self.cleaner_state.angle

    def get_state(self):
        return self.cleaner_state.state

    def activate_cleaner(self, code):
        for command in code:
            cmd = command.split(" ")
            if cmd[0] == "move":
                self.cleaner_state = self._cleaner.move(
                    self.transfer_to_cleaner, int(cmd[1]), self.cleaner_state
                )
            elif cmd[0] == "turn":
                self.cleaner_state = self._cleaner.turn(
                    self.transfer_to_cleaner, int(cmd[1]), self.cleaner_state
                )
            elif cmd[0] == "set":
                self.cleaner_state = self._cleaner.set_state(
                    self.transfer_to_cleaner, cmd[1], self.cleaner_state
                )
            elif cmd[0] == "start":
                self.cleaner_state = self._cleaner.start(
                    self.transfer_to_cleaner, self.cleaner_state
                )
            elif cmd[0] == "stop":
                self.cleaner_state = self._cleaner.stop(
                    self.transfer_to_cleaner, self.cleaner_state
                )


if __name__ == "__main__":
    cleaner_api = CleanerApi(
        pure_robot, pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER)
    )

    cleaner_api.activate_cleaner(
        ("move 100", "turn -90", "set soap", "start", "move 50", "stop")
    )

print(
    cleaner_api.get_x(),
    cleaner_api.get_y(),
    cleaner_api.get_angle(),
    cleaner_api.get_state(),
)
