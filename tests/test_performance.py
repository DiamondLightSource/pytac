import time

import pytac


async def test_asyncio():
    pytac_lattice = await pytac.load_csv.load("I04", symmetry=24)
    start = time.time()
    for _ in range(100):
        await pytac_lattice.get_element_values("Quadrupole", "b1", pytac.RB)
    end = time.time()
    print(f"Time taken: {end - start}")
    raise AssertionError()


async def test_cothread():
    pytac_lattice = pytac.load_csv.load("I04", symmetry=24)
    start = time.time()
    for _ in range(100):
        pytac_lattice.get_element_values("Quadrupole", "b1", pytac.RB)
    end = time.time()
    print(f"Time taken: {end - start}")
    raise AssertionError()
