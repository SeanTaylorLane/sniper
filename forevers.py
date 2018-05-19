import asyncio
import functools

def foo():
    print("Hi!")

def event_handler(loop, stop=False):
    foo()
    if stop:
        loop.stop()

loop = asyncio.get_event_loop()
while True:
    loop.call_later(1, foo)
    loop.run_forever()
