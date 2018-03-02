import pytest
import logging
import asyncio
from aioreactive.core import run, AsyncAnonymousObserver
from aioreactive.operators import from_iterable, from_async_iterable, retry, catch_exception

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


async def iter_error():
    for i in range(5):
        await asyncio.sleep(1)
        yield i
    raise ValueError("Test Exception")



@pytest.mark.asyncio
async def test_retry():
    xs = from_async_iterable(iter_error())
    result = []

    async def asend(value):
        print("ASEND", value)
        log.debug("test_retry:asend(%s)", value)
        result.append(value)

    zs = catch_exception([xs])

    await run(zs, AsyncAnonymousObserver(asend))
    assert result == list(range(10))

