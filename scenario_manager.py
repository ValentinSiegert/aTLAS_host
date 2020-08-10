from multiprocessing.managers import SyncManager
from models import Scenario


class ScenarioManager(SyncManager):
    pass

ScenarioManager.register('Scenario', Scenario)

