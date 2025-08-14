Quickstart
==========


Installation
------------

Use pip to install the lastest version:

.. code-block:: bash

    pip install inject



No config usage
---------------

For the simplest case, these three steps are sufficient.

#. Define injection target (your example function) with ``autoparams`` decorator
#. Wire injections with ``configure``
#. Use your function!

.. code-block:: python

    import inject

    class RedisCache:
        def __init__(self, endpoint: str = "localhost:6379"): self._endpoint = endpoint
        def refresh(self): print(f"Refreshing cache for {self._endpoint}...")

    class DbInterface:
        def reset(self): print(f"Resetting db using {self.__class__.__name__}...")

    class DbInterface2(DbInterface): ...


    @inject.autoparams
    def refresh_cache(cache: RedisCache, db: DbInterface):
        cache.refresh()
        db.reset()


    inject.configure()

    refresh_cache()
    # Refreshing cache for localhost:6379...
    # Resetting db using DbInterface...


**Inject uses type hints to determine injections.**

By default, ``inject`` creates an injection by calling its type with no arguments.
So for this simple case you don't have to configure anything special.


**You may explicitly pass your argument** and it will be used instead of injection.

.. code-block:: python

    refresh_cache(db=DbInterface2())
    # Refreshing cache for localhost:6379...
    # Resetting db using DbInterface2...


Now let's make it a little more interesting!


More interesting cases
----------------------

So, we've covered decorating functions, but what about classes?
— Their **methods can be decorated too!**
Moreover, you can **attach fields** (descriptors) to your classes to access injections
when accessing instance attributes.

Also, we can **configure our injections manually** — to do this, we need to **provide
a special callable** for ``configure``.
This callable should accept a :ref:`binder object<Binder_label>` and bind all your sources.

This example uses only 2 main wiring options
(others can be found in :ref:`specifications<Specifications_label>`)
— the **instance** and **factory** bindings.

Let's try all this now!

.. code-block:: python

    import os, inject

    class RedisCache:
        def __init__(self, endpoint: str = "localhost:6379"): self._endpoint = endpoint
        def refresh(self): print(f"Refreshing cache for {self._endpoint}...")

    class DbInterface:
        def reset(self, table='default'): print(f"Resetting db {table} using {self.__class__.__name__}...")

    class DbInterface2(DbInterface): ...


    class MyEntity:
        cache: RedisCache = inject.attr()
        db: DbInterface = inject.attr(DbInterface2)

        @inject.autoparams
        def refresh_cache(self, cache: RedisCache, db: DbInterface):
            cache.refresh()
            db.reset()

        @inject.autoparams('cache')
        def refresh_cache_with_manual_db(self, cache: RedisCache, db: DbInterface):
            cache.refresh()
            db.reset()


    db_instance = DbInterface2()

    def _cache_factory():
        endpoint_from_config = os.environ.get("REDIS_ENDPOINT", "127.0.0.1:6379")
        return RedisCache(endpoint=endpoint_from_config)

    def wire(binder):
        # bind instance: configure shared instance
        binder.bind(DbInterface2, db_instance)

        # bind factory: configure factory (will be called once
        #               and returned instance will be shared during injections)
        binder.bind_to_constructor(RedisCache, _cache_factory)

    inject.configure(wire)

    my_object = MyEntity()
    my_object.refresh_cache()
    # Refreshing cache for 127.0.0.1:6379...
    # Resetting db default using DbInterface...


Okay, our main case is still working.

Let's check out injected instance attributes:

.. code-block:: python

    my_object.cache
    # <__main__.RedisCache object at 0x7b78086097f0>
    my_object.cache.refresh()
    # Refreshing cache for 127.0.0.1:6379...
    my_object.db
    # <__main__.DbInterface2 object at 0x7b78086082f0>
    my_object.db.reset()
    # Resetting db default using DbInterface2...


Great! They work as expected.

What about our ``DbInterface2`` instance? - Is it the same (our variable and instance attribute)?

.. code-block:: python

    db_instance is my_object.db
    # True


Yes, it is! So we can move forward.

We didn't provide manual binding for ``DbInterface``, so the type constructor is used by default.

We have also limited the arguments allowed to be injected into ``refresh_cache_with_manual_db`` method
— so ``inject`` will only register the ``cache`` argument
and you must always specify the ``db`` argument when calling this method.

Let's call it first with the ``db`` argument, and then without it.

.. code-block:: python

    my_object.refresh_cache_with_manual_db(db=DbInterface2())
    # Refreshing cache for 127.0.0.1:6379...
    # Resetting db default using DbInterface2...


Perfect! It works.

.. code-block:: python

    my_object.refresh_cache_with_manual_db()
    # Traceback (most recent call last):
    #   ...
    # TypeError: MyEntity.refresh_cache_with_manual_db() missing 1 required positional argument: 'db'
    # During handling of the above exception, another exception occurred:
    # Traceback (most recent call last):
    #   ...
    #     raise ConstructorTypeError(func, previous_error)
    # inject.ConstructorTypeError: <function MyEntity.refresh_cache_with_manual_db at 0x7b78086584a0> raised an error: MyEntity.refresh_cache_with_manual_db() missing 1 required positional argument: 'db'


It failed. As we should have expected.

Another thing to play with is that you can directly access the injection by asking ``inject`` for it:

.. code-block:: python

    inject.instance(DbInterface2)
    # <__main__.DbInterface2 at 0x7b78086082f0>


That's probably enough to get you started.

**More details in the** :ref:`Specifications section<Specifications_label>`.
