from utils.threads.threads import Threads


class TournamentsThread(Threads):
    def __init__(self, name):
        super().__init__(name)

    async def main(self):
        pass

    def cleanup(self):
        pass
