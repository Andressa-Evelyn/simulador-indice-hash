import asyncio
from typing import Callable, TypeVar, Awaitable, Union
from edifice import use_state, use_async


T = TypeVar("T")


def use_debouce_state(
    initial_value: T,
    func: Callable[[T], Union[None, Awaitable[None]]],
    interval: int = 800,
) -> tuple[T, Callable[[T], None]]:
    value, set_value = use_state(initial_value)

    async def debounce():
        await asyncio.sleep(interval / 1000)
        res = func(value)
        if asyncio.iscoroutine(res):
            await res

    use_async(debounce, dependencies=value)

    return value, set_value

