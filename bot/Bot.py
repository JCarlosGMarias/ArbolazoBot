#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import json
import random


class Bot:
    __slots__ = ["speech", "definitions", "animations", "root", "tree", "offset"]

    def __init__(self):
        self.speech = [
            "Con afecto (y con efecto)",
            "Te lo mereces más que nadie",
            "Aprovecha y planta esto",
            "Lo estabas pidiendo a gritos...",
            "Tú nunca aprendes, verdad?"
        ]
        self.definitions = [
            "vacacion",
            "vacación",
            "vacaci'on",
            "vacaciones",
            "vacasiones",
            "vacances",
            "holiday",
            "holidays"
        ]
        self.animations = [
            "CgADBAADDAEAAoyISVIPbiFidT63fQI",
            "CgADBAAD7rAAAmkeZAdHvre6NP-p7wI"
        ]

        with open("./config.json") as config_file:
            config = json.load(config_file)

            self.root = f"https://api.telegram.org/bot{config['token']}"
            self.tree = config['tree']

        self.offset = 0

    def execute(self) -> None:
        loop = asyncio.get_event_loop()

        try:
            asyncio.ensure_future(self._work())
            loop.run_forever()
        except KeyboardInterrupt:
            print("Bot was interrupted!")
        finally:
            print("Closing loop...")
            loop.close()

    async def _work(self) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                response = await self._get_updates(session)

                updates = json.loads(response)["result"]

                for update in updates:
                    self.offset = update["update_id"] + 1

                    msg = update["message"]

                    message_id = msg["message_id"]
                    chat_id = msg["chat"]["id"]

                    try:
                        if "text" in msg:
                            await self._handle_text(session, msg["text"], message_id, chat_id)
                        elif "animation" in msg:
                            await self._handle_animation(session, msg["animation"], message_id, chat_id)
                    except KeyError:
                        print("Unrecognized key in message")

                await asyncio.sleep(4)
                print("Task executed. Polling again...")

    async def _handle_text(self, session: aiohttp.ClientSession, content: str, sender: str, chat: str) -> None:
        for word in self.definitions:
            if word in content.lower():
                await self._send_tree(session, sender, chat)
                break

    async def _handle_animation(self, session: aiohttp.ClientSession, content: {}, sender: str, chat: str):
        if content["file_id"] in self.animations:
            await self._send_tree(session, sender, chat)

    async def _send_tree(self, session: aiohttp.ClientSession, sender: str, chat: str) -> None:
        animation = {
            "chat_id": chat,
            "animation": self.tree,
            "reply_to_message_id": sender,
            "caption": self.speech[random.randint(0, len(self.speech) - 1)]
        }

        async with session.post(self.root + "/sendAnimation", json=animation) as response:
            await response.text()

    async def _get_updates(self, session: aiohttp.ClientSession) -> str:
        async with session.get(self.root + "/getUpdates", data={"offset": self.offset}) as response:
            return await response.text()
