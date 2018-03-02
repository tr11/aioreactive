from typing import Generic, TypeVar, Iterable
import asyncio
import logging

from aioreactive.core import AsyncDisposable, AsyncCompositeDisposable
from aioreactive.core import AsyncObserver, AsyncObservable
from aioreactive.core import AsyncSingleStream, chain

log = logging.getLogger(__name__)
T = TypeVar('T')


class CatchException(AsyncObservable[T], Generic[T]):

    def __init__(self, iterable) -> None:
        super().__init__()
        self._iterable = iter(iterable)
        self._subscription = None  # type: AsyncDisposable
        self._task = None  # type: asyncio.Future
        self._stop = False

    async def worker(self, observer: AsyncObserver) -> None:
        def recurse(fut) -> None:
            if self._stop:
                log.debug("CatchException._:stop")
                print("STOP")
                asyncio.ensure_future(observer.aclose())
            else:
                log.debug("CatchException._:continue to next iterable")
                print("NO STOP")
                self._task = asyncio.ensure_future(self.worker(observer))
        try:
            source = next(self._iterable)
        except StopIteration:
            await observer.aclose()
        except Exception as ex:
            await observer.athrow(ex)
        else:
            self._stop = True
            sink = CatchException.Stream(self)
            down = await chain(sink, observer)  # type: AsyncDisposable
            up = await chain(source, sink)
            sink.add_done_callback(recurse)
            self._subscription = AsyncCompositeDisposable(up, down)

    async def __asubscribe__(self, observer: AsyncObserver) -> AsyncDisposable:
        async def cancel() -> None:
            log.debug("CatchException._:__asubscribe__ cancel")
            if self._subscription is not None:
                await self._subscription.adispose()

            if self._task is not None:
                self._task.cancel()

        self._task = asyncio.ensure_future(self.worker(observer))
        return AsyncDisposable(cancel)

    class Stream(AsyncSingleStream):

        def __init__(self, outer):
            super().__init__()
            self._outer = outer

        async def aclose(self) -> None:
            log.debug("CatchException._:close()")
            self._outer._stop = True
            self.cancel()

        async def athrow(self, ex: Exception) -> None:
            log.debug("CatchException._:athrow()")
            self._outer._stop = False
            self.cancel()


def catch_exception(iterable: Iterable[T]) -> AsyncObservable[T]:
    return CatchException(iterable)
