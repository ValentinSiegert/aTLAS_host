import websockets
from connectors.basic_connector import BasicConnector
import json
import asyncio
from time import sleep


class ChannelsConnector(BasicConnector):
    async def register_at_director(self):
        print("Registering at Director...")
        await self.connect_web_socket()
        await self.set_max_agents()
        print("Fully Registered at Director")

    async def connect_web_socket(self):
        connection_attempts = 0
        while self.websocket is None:
            try:
                self.websocket = await websockets.client.connect(self.director_uri)
            except ConnectionRefusedError:
                sleep(5 + connection_attempts * 2)
                connection_attempts = connection_attempts + 1

    async def set_max_agents(self):
        register_max_agents = {"type": "max_agents", "max_agents": self.max_agents}
        await self.send_json(register_max_agents)
        await self.receive_json()

    async def send_json(self, message):
        await self.websocket.send(json.dumps(message))

    async def receive_json(self):
        return await self.websocket.recv()

    async def consumer_handler(self):
        async for message in self.websocket:
            message_json = json.loads(message)
            if message_json["type"] == "scenario_registration":
                await self.pipe_dict["supervisor"].coro_send(message_json)
            elif message_json["scenario_run_id"] in self.pipe_dict.keys() \
                    and not message_json["type"] == "scenario_registration":
                await self.pipe_dict[message_json["scenario_run_id"]].coro_send(message_json)
            else:
                # TODO implement what happens if message does not fit in another case
                pass

    async def producer_handler(self):
        while True:
            message = await self.send_queue.coro_get()
            await self.websocket.send(json.dumps(message))

    async def handler(self):
        consumer_task = asyncio.ensure_future(self.consumer_handler())
        producer_task = asyncio.ensure_future(self.producer_handler())
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.ALL_COMPLETED)
        for task in pending:
            task.cancel()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.register_at_director())
        asyncio.get_event_loop().run_until_complete(self.handler())

    def __init__(self, director_hostname, max_agents, send_queue, pipe_dict):
        super().__init__(director_hostname, max_agents, send_queue, pipe_dict)
        self.director_uri = "ws://" + self.director_hostname + "/supervisors/"
        self.websocket = None



