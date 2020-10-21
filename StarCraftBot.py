import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER

class SCBot(sc2.BotAI):

    # code executed on every step
    async def on_step(self, iteration):

        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.build_offensive_buildings()
        await self.train_units()

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

    # function for constructing assimilators, a structure required to gather
    # one in game resource
    async def build_assimilators(self):

        if self.units(PYLON).ready.exists or self.already_pending(PYLON):

            for nexus in self.units(NEXUS).ready:

                geysers = self.state.vespene_geyser.closer_than(10.0, nexus)

                for geyser in geysers:

                    if not self.can_afford(ASSIMILATOR):
                        break

                    worker = self.select_build_worker(geyser.position)

                    if worker is None:
                        break

                    if not self.units(ASSIMILATOR).closer_than(1.0, geyser).exists:
                        await self.do(worker.build(ASSIMILATOR, geyser))

    # function for expanding to new map locations
    # necessary for acquiring additional resources
    async def expand(self):

        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    # function for building offensive buildings
    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:

            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists:

                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
            else:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

    # function for handling the creation of offensive units
    async def train_units(self):

        for gateway in self.units(GATEWAY).ready.noqueue:

            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.do(gateway.train(STALKER))

def main():
    sc2.run_game(
        sc2.maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss, SCBot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=True,
    )

main()
