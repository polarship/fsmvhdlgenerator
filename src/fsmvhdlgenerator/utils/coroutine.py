"""Defines utilities for generator-based coroutines.

Tkinter uses callbacks for event handling, which is inconvenient when
one wants to save state in between calls (like, for instance, an item's
position as it is being moved). These utilities make working with
callbacks easier using by allowing generator coroutines to be used like
callbacks.

"""

import logging
from typing import Callable


def coroutine(end_behavior: str = 'loop',
              iteration_decorator: Callable = lambda x: x):
    """Encapsulate a generator to make coroutine callbacks.

    Wrapped around a generator function, the generator will now iterate
    from ordinary function calls on the wrapped function name, rather
    than "send" and "next" method calls. Once the generator empties, a
    new generator from the decorated function will be created.

    End behavior is controlled with a keyword argument. Calls to the
    generator can pass an argument which will be what is sent by the
    send method

    Args:
        end_behavior: If set to "loop", will cause the generator's "send"
            method to be called immediately after the generator is recreated
        iteration_decorator: a decorator for use on each iteration of the
            generator, filtering the value sent to the generator

    Returns:
        coroutine_definition: a coroutine suitable for use as a callback.

    """
    def coroutine_definition(generator_func):
        """Return a callable that can be called to iterate the generator.

        Args:
            generator_func: The generator function to create the coroutine from

        """
        def coroutine_initialization(*args, **kwargs):
            """Initialize the coroutine and prepare it for future calls.

            Starts the generator function with passed arguments and iterates it
            once to prepare it to receive subsequent passed arguments.

            Args:
                *args: Passed to generator_func()
                **kwargs: Passed to generator_func()

            """
            logging.info("Initializing coroutine with args %s, kwargs %s",
                         args, kwargs)
            gen = generator_func(*args, **kwargs)
            next(gen)

            def coroutine_iteration(event):
                """Iterate the generator by sending it the argument event.

                Each non-initial call of the function this decorator applies to
                runs this function. Generally, this is called by an event
                handler, passing it an event as an argument.

                Iteration continues until StopIteration, at which point the
                generator is reset, with behavior controlled by end_behavior.

                Args:
                    event: Sent to the generator function

                Returns:
                    The yielded values of the generator function

                """
                nonlocal gen

                try:
                    logging.debug("Sending event %s for coroutine iteration",
                                  event)
                    return gen.send(event)

                except StopIteration:  # Controls coroutine exhaustion behavior
                    logging.debug("Re-initializing coroutine")
                    gen = generator_func(*args, **kwargs)
                    next(gen)
                    logging.info("Sending event %s for coroutine iteration",
                                 event)
                    if end_behavior == 'loop':
                        return gen.send(event)

            return iteration_decorator(coroutine_iteration)

        return coroutine_initialization

    return coroutine_definition
