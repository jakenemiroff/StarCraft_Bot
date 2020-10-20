import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON

class SCBot(sc2.BotAI):

    # code executed on every step
    async def on_step(self, iteration):

        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()

        # code responsible for building worker units
    async def build_workers(self):

        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    # code for building pylons, a protoss structure enabling other buildings
    # to be built, and to increase supply cap
    async def build_pylons(self):

        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

def main():
    sc2.run_game(
        sc2.maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss, SCBot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=True,
    )

main()
