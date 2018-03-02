import pytest
import logging

import asyncio
from aioreactive.core import run, AsyncAnonymousObserver
from aioreactive.operators import from_iterable, from_async_iterable, catch_exception
from aioreactive.testing import VirtualTimeEventLoop

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


async def iter_error():
    for i in range(5):
        await asyncio.sleep(1)
        yield i
    raise ValueError("Test Exception")


@pytest.yield_fixture()
def event_loop():
    loop = VirtualTimeEventLoop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_catch_one():
    xs = from_iterable(range(0, 5))
    result = []

    async def asend(value):
        log.debug("test_catch_one:asend(%s)", value)
        result.append(value)

    zs = catch_exception([xs])

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(5))


@pytest.mark.asyncio
async def test_catch_one_with_error():
    xs = from_async_iterable(iter_error())
    result = []

    async def asend(value):
        log.debug("test_catch_one_with_error:asend(%s)", value)
        result.append(value)

    zs = catch_exception([xs])

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(5))


@pytest.mark.asyncio
async def test_catch_no_error():
    xs = from_iterable(range(0, 5))
    ys = from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_catch_no_error:asend(%s)", value)
        result.append(value)

    zs = catch_exception((xs, ys))

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(5))


@pytest.mark.asyncio
async def test_catch_with_error():
    xs = from_async_iterable(iter_error())
    ys = from_iterable(range(5, 10))
    result = []

    async def asend(value):
        log.debug("test_catch_with_error:asend(%s)", value)
        result.append(value)

    zs = catch_exception((xs, ys))

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))
    assert False

