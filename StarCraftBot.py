import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random

class SCBot(sc2.BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165

    # code executed on every step
    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.build_offensive_buildings()
        await self.train_units()
        await self.attack()

    # code responsible for building worker units
    async def build_workers(self):

        for nexus in self.units(NEXUS).ready.noqueue:
            if self.workers.amount < self.units(NEXUS).amount * 15 and nexus.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    # code for building pylons, a protoss structure enabling other buildings
    # to be built, and to increase supply cap
    async def build_pylons(self):

        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready

            if nexuses.exists:

                if self.can_afford(PYLON):
                    await self.build(PYLON, near = nexuses.first)

    # function for constructing assimilators, a structure required to gather
    # one in game resource
    async def build_assimilators(self):

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

        if self.units(NEXUS).amount < 3 and not self.already_pending(NEXUS) and len(self.units(NEXUS)) < ((self.iteration / self.ITERATIONS_PER_MINUTE) / 2.5):
            if self.can_afford(NEXUS):
                await self.expand_now()

    # function for building offensive buildings
    async def build_offensive_buildings(self):

        map_center = self.game_info.map_center
        position_towards_map_center = self.start_location.towards(map_center, distance = 8)

        if self.units(PYLON).ready.exists:

            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near = position_towards_map_center, placement_step = 1)

            elif len(self.units(GATEWAY)) < (self.iteration / self.ITERATIONS_PER_MINUTE) / 3:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:

                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE) / 5) and len(self.units(STARGATE)) < 4:
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near = pylon)

                if len(self.units(ROBOTICSFACILITY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE) / 5) and len(self.units(ROBOTICSFACILITY)) < 4:
                    if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                        await self.build(ROBOTICSFACILITY, near = pylon)

    # function for handling the creation of offensive units
    async def train_units(self):

        for starGate in self.units(STARGATE).ready.noqueue:

            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(starGate.train(VOIDRAY))

        for roboticsFacility in self.units(ROBOTICSFACILITY).ready.noqueue:

            if self.can_afford(IMMORTAL) and self.supply_left > 0:
                await self.do(roboticsFacility.train(IMMORTAL))

        for gateway in self.units(GATEWAY).ready.noqueue:

            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.do(gateway.train(STALKER))

            elif self.can_afford(ZEALOT) and self.supply_left > 0:
                await self.do(gateway.train(ZEALOT))


    async def attack(self):

        units = [ZEALOT, STALKER, VOIDRAY, IMMORTAL, COLOSSUS]

        for unit in units:
            if self.army_count > 35:
                for specificUnit in self.units(unit).idle:
                    await self.do(specificUnit.attack(self.scout(self.state)))

            elif len(self.known_enemy_units) > 0:
                    for specificUnit in self.units(unit).idle:
                        await self.do(specificUnit.attack(random.choice(self.known_enemy_units)))

    def scout(self, state):

        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)

        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)

        else:
            return random.choice(self.enemy_start_locations)

def main():
    sc2.run_game(
        sc2.maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss, SCBot()), Computer(Race.Zerg, Difficulty.Hard)],
        realtime=False,
    )

main()
