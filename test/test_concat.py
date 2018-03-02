import pytest
import asyncio
import logging

from aioreactive.core import AsyncObservable, run, AsyncAnonymousObserver
from aioreactive.operators import from_iterable, concat, from_async_iterable
from aioreactive.testing import VirtualTimeEventLoop

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@pytest.yield_fixture()
def event_loop():
    loop = VirtualTimeEventLoop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_concat_happy():
    xs = from_iterable(range(5))
    ys = from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_concat_happy:send(%s)", value)
        result.append(value)

    zs = concat(xs, ys)

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))


@pytest.mark.asyncio
async def test_concat_special_add():
    xs = AsyncObservable.from_iterable(range(5))
    ys = AsyncObservable.from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_concat_special_add:asend(%s)", value)
        result.append(value)

    zs = xs + ys

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))


@pytest.mark.asyncio
async def test_concat_special_iadd():
    xs = AsyncObservable.from_iterable(range(5))
    ys = AsyncObservable.from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_concat_special_iadd:asend(%s)", value)
        result.append(value)

    xs += ys

    await run(xs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))


async def asynciter():
    for i in range(5):
        await asyncio.sleep(1)
        yield i


@pytest.mark.asyncio
async def test_concat_async():
    xs = from_async_iterable(asynciter())
    ys = from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_concat_async:send(%s)", value)
        result.append(value)

    zs = concat(xs, ys)

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_concat_happy())
    loop.close()
