import queue
import threading
import pure_robot


class RobotCommand:

    def __init__(self, input_state, command, func):
        self.state = input_state
        self.command = command
        self.func = func


class ThreadRobo(threading.Thread):
    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            command = self.queue.get()
            cleaner_state = command.state
            cmd = command.command.split(" ")

            if cmd[0] == "move":
                cleaner_state = command.func(
                    pure_robot.transfer_to_cleaner, int(cmd[1]), cleaner_state
                )
            elif cmd[0] == "turn":
                cleaner_state = command.func(
                    pure_robot.transfer_to_cleaner, int(cmd[1]), cleaner_state
                )
            elif cmd[0] == "set":
                cleaner_state = command.func(
                    pure_robot.transfer_to_cleaner, cmd[1], cleaner_state
                )
            elif cmd[0] == "start":
                cleaner_state = command.func(
                    pure_robot.transfer_to_cleaner, cleaner_state
                )
            elif cmd[0] == "stop":
                cleaner_state = command.func(
                    pure_robot.transfer_to_cleaner, cleaner_state
                )
            else:
                continue

            rez = RobotCommand(
                input_state=cleaner_state, command="RESULT", func=command.func
            )
            self.out_queue.put(rez)
            self.queue.task_done()


if __name__ == "__main__":
    # Сервер
    num_workers = 5

    in_queue = queue.Queue()
    out_queue = queue.Queue()

    for i in range(num_workers):
        t = ThreadRobo(in_queue, out_queue)
        t.daemon = True
        t.start()

    # Клиент
    def command_to_queue(command):
        in_queue.put(command)
        chunk = out_queue.get()
        out_queue.task_done()
        return chunk

    c = RobotCommand(
        input_state=pure_robot.RobotState(0.0, 0.0, 0, pure_robot.WATER),
        command="move 100",
        func=pure_robot.move,
    )
    c = command_to_queue(c)

    c.command = "turn -90"
    c.func = pure_robot.turn
    c = command_to_queue(c)

    c.command = "set soap"
    c.func = pure_robot.set_state
    c = command_to_queue(c)

    c.command = "start"
    c.func = pure_robot.start
    c = command_to_queue(c)

    c.command = "move 50"
    c.func = pure_robot.move
    c = command_to_queue(c)

    c.command = "stop"
    c.func = pure_robot.stop
    c = command_to_queue(c)

    for i in range(1000):
        c.command = "turn -90"
        c.func = pure_robot.turn
        c = command_to_queue(c)

    print(c.state.x)
