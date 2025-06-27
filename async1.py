import asyncio
import time


async def one():
    await asyncio.sleep(1)
    print("Returning from one()")
    return "message from one"

# async def two(text):
async def two():
    text = "hard coded text"
    await asyncio.sleep(5)
    print("Returning from two()")
    return f"{text} and message from two"

async def three():
    start = time.perf_counter()
    # Await method
    # result_one = await one()
    # result = await two()

    # Task Method
    task1 = asyncio.create_task(one())
    task2 = asyncio.create_task(two())


    
    # Gather Method
    # results = await asyncio.gather(one(), two())
    end = time.perf_counter() - start
    print(f"-->Chained result from three => {result} (took {end:0.2f} seconds).")
    return result


async def main():
    results = await three()
    print(results)


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter() - start
    print(f"Program finished in {end:0.2f} seconds.")

