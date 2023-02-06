import asyncio
import sys
from asyncio import sleep, CancelledError, TimeoutError
from datetime import datetime
from typing import Optional, Literal

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError


DEFAULT_THREADS_COUNT = 1000
DELAY = 0.2
ADDRESS = 'ws://127.0.0.1:8000/ws'


def print_message(msg: str, color: Optional[Literal['green', 'red', 'orange', 'magenta']] = None) -> None:
    color_templates = {
        'green': '\033[0;32m{}\033[00m',
        'blue': '\033[0;94m{}\033[00m',
        'red': '\033[0;31m{}\033[00m',
        'magenta': '\033[0;35m{}\033[00m'
    }
    tpl = color_templates.get(color, '{}')
    tpl = f'{datetime.now().isoformat()} {tpl}'
    msg = tpl.format(msg)
    print(msg)


async def run_socket(url: str, index: Optional[int] = 1) -> None:
    cancelled = False

    # Initial delay for connection
    await sleep(DELAY * index)

    retry = 0
    while not cancelled:
        retry += 1
        last_message = None
        try:
            if retry == 1:
                msg = f"[{index}] Connected to websocket"
                color = 'green'
            else:
                msg = f"[{index}, retry: {retry}] Reconnected to websocket"
                color = 'magenta'
            async with websockets.connect(url) as websocket:
                print_message(msg, color=color)
                async for message in websocket:
                    last_message = message
                    # print_message(f'[{index}] Got message {message}', color='magenta)
                    await sleep(1)
        except (CancelledError, ConnectionClosedOK) as ex:
            cancelled = True
        except (ConnectionClosedError, TimeoutError) as ex:
            msg = f'ConnectionClosedError({str(ex)})' if isinstance(ex, ConnectionClosedError) else repr(ex)
            print_message(f'[{index}] Closed connection, restarting: ex: {msg}, last message: {last_message}',
                          color='red')

        except Exception as ex:
            print_message(f'Unhandled exception [{index}, {url}]: {repr(ex)}', color='red')
            raise ex


async def main() -> None:
    threads_count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_THREADS_COUNT
    print(f'Starting with {threads_count} threads, delay {DELAY} seconds')
    await asyncio.gather(*(
        run_socket(ADDRESS, index=i) for i in range(threads_count)
    ))


asyncio.run(main())
