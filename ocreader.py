#!/usr/bin/env python3

import asyncio
from json import load
from nio import AsyncClient, RoomMessageText
import re
import klembord

CONFIG = load(open('config.json'))

RE_CLEANUP = [(re.compile(r'\s+,\s+'), ', '),
              (re.compile(r'\s+;\s+'), '; '),
              (re.compile(r'\s+\(\s+'), ' ('),
              (re.compile(r'\s+\)'), ')'),
              ]


def cleanup_message(message: str) -> str:
    for regex, replacement in RE_CLEANUP:
        message = regex.sub(replacement, message)
    return message


def format_message(message: str) -> str:
    content = []
    is_enumerated = False
    for line in message.split('\n'):
        line = line.strip()
        if is_enumerated and line and not line.startswith('-'):
            is_enumerated = False
            content.append('</ul>')
        if line.startswith('#'):
            content.append(f'<h1>{line[1:]}</h1>')
        elif line == 'Summary':
            content.append(f'<h1>{line}</h1>')
        elif line.startswith('-'):
            if not is_enumerated:
                content.append('<ul>')
                is_enumerated = True
            content.append(f'<li>{line[1:].strip()}</li>')
        elif line:
            content.append(line + '</br>')

    content ='\n'.join(content)
    print(content)
    return f'<html><body>{content}</body></html>'


async def receive_message(room, event):
    print(room.name)
    if room.name == 'OCR':
        message = cleanup_message(event.body)
        print("Message:", message)
        klembord.set_with_rich_text(text=message,
                                    html=format_message(message))


async def main():
    client = AsyncClient(CONFIG['matrix_homeserver'])
    client.access_token = CONFIG['matrix_access_token']
    client.user_id = CONFIG['matrix_user_id']

    client.add_event_callback(receive_message, RoomMessageText)

    await client.sync_forever(timeout=30000)

asyncio.get_event_loop().run_until_complete(main())
