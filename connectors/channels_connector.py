import asyncio
import json
import websockets
from connectors.basic_connector import BasicConnector
from time import sleep


class ChannelsConnector(BasicConnector):
    async def register_at_director(self):
        print("Registering at Director...")
        await self.connect_web_socket()
        await self.set_max_agents()
        print(f"Fully Registered a capacity of max. {self.max_agents} agents at Director.")

    async def register_as_evaluator(self):
        print('Registering as evaluator...')
        await self.connect_web_socket()
        await self.send_json({'type': 'register_eval_run'})
        await self.receive_json()
        print('Fully Registered at Director and locked WebUI.')

    async def connect_to_director(self):
        print("Connecting to Director...")
        await self.connect_web_socket()
        print("Connected to Director.")

    async def connect_web_socket(self):
        connection_attempts = 0
        while self.websocket is None:
            try:
                self.websocket = await websockets.connect(self.director_uri)
            except ConnectionRefusedError:
                sleep(5 + connection_attempts * 2)
                connection_attempts = connection_attempts + 1

    async def set_max_agents(self):
        register_max_agents = {"type": "max_agents", "max_agents": self.max_agents}
        register_max_agents.update(self.supervisor_info)
        await self.send_json(register_max_agents)
        await self.receive_json()

    async def send_json(self, message):
        await self.websocket.send(json.dumps(message))

    async def receive_json(self):
        return await self.websocket.recv()

    async def consuming_message(self, message):
        """
        Consuming the full message received from the websocket.

        :param message: The complete received message as JSON object.
        :type message: dict or list
        """
        if 'evaluator' in self.pipe_dict.keys():
            await self.pipe_dict["evaluator"].coro_send(message)
        elif message["type"] == "scenario_registration":
            await self.pipe_dict["supervisor"].coro_send(message)
        elif message["scenario_run_id"] in self.pipe_dict.keys() \
                and not message["type"] == "scenario_registration":
            await self.pipe_dict[message["scenario_run_id"]].coro_send(message)
        else:
            # TODO implement what happens if message does not fit in another case,
            #  chunked transfer require similar handling
            pass

    async def consuming_chunked_transfer(self, message):
        """
        Consuming the messages which are part of the chunked transfer via the websocket.

        :param message: The received message as JSON object, where type has to be 'chunked_transfer'.
        :return: dict or list
        """
        print(f'Received part {message["part_number"][0]}/{message["part_number"][1]} ...')
        if not self.chunked_parts and message['part_number'][0] == 1:
            self.chunked_parts = message['part']
        elif self.chunked_parts and message['part_number'][0] <= message['part_number'][1]:
            self.chunked_parts += message['part']
        else:
            print('ChannelsConnector received chunked transfer with unexpected status.')
            print(f'Chunked parts {"exist" if self.chunked_parts else "do NOT exist"} '
                  f'while message indicates part {message["part_number"]}.')
        await self.send_json({'type': 'chunked_transfer_ack', 'part_number': message['part_number']})
        print(f'Send "chunked_transfer_ack" message for {message["part_number"][0]}/{message["part_number"][1]}')
        if message['part_number'][0] == message['part_number'][1]:
            actual_message = json.loads(self.chunked_parts)
            self.chunked_parts = None
            await self.consuming_message(actual_message)

    async def consumer_handler(self):
        async for message in self.websocket:
            message_json = json.loads(message)
            if message_json['type'] == 'chunked_transfer':
                await self.consuming_chunked_transfer(message_json)
            elif message_json['type'] == 'end_socket':
                return
            else:
                await self.consuming_message(message_json)

    async def producer_handler(self):
        while True:
            message = await self.send_queue.coro_get()
            await self.send_json(message)
            if message['type'] == 'end_socket':
                return

    async def handler(self):
        consumer_task = asyncio.ensure_future(self.consumer_handler())
        producer_task = asyncio.ensure_future(self.producer_handler())
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.ALL_COMPLETED)
        for task in pending:
            task.cancel()

    def run(self):
        if self.no_registration:
            asyncio.get_event_loop().run_until_complete(self.connect_to_director())
        else:
            if self.max_agents > 0:
                asyncio.get_event_loop().run_until_complete(self.register_at_director())
            else:
                asyncio.get_event_loop().run_until_complete(self.register_as_evaluator())
        asyncio.get_event_loop().run_until_complete(self.handler())

    def __init__(self, director_hostname, max_agents, send_queue, pipe_dict, sec_conn, supervisor_info=None,
                 no_registration=False):
        super().__init__(director_hostname, max_agents, send_queue, pipe_dict, sec_conn, supervisor_info)
        self.director_uri = f"{'wss://' if sec_conn else 'ws://'}{self.director_hostname}" \
                            f"{'/lab/' if max_agents==0 else'/supervisors/'}"
        self.websocket = None
        self.chunked_parts = None
        self.no_registration = no_registration
