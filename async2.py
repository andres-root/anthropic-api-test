import asyncio
import random

# --- Coroutines are the same as before ---

async def one():
    """Returns True if task2 should proceed, False otherwise."""
    sleep_time = random.uniform(0.5, 1)
    print(f"Task 1: Starting, will run for {sleep_time:.2f} seconds.")
    await asyncio.sleep(1)
    # should_continue = random.choice([True, False])
    should_continue = True
    print(f"Task 1: Finished. Result: 'should_continue' is {should_continue}")
    return should_continue, "data"

async def two():
    """A slower task that might be cancelled."""
    sleep_time = random.uniform(2, 3)
    print(f"Task 2: Starting, will run for {sleep_time:.2f} seconds.")
    try:
        await asyncio.sleep(3)
        print("Task 2: Finished successfully.")
        return "Task 2 Data" # Return a meaningful result
    except asyncio.CancelledError:
        print("Task 2: I was cancelled!")
        raise

# --- The NEW Orchestration Logic ---

async def main():
    print("--- Starting main orchestration ---")
    
    # Variables to hold the results
    result1 = None
    result2 = None

    task1 = asyncio.create_task(one(), name="Task 1")
    task2 = asyncio.create_task(two(), name="Task 2")

    tasks = {task1, task2}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Process the first completed task (expected to be task1)
    if task1 in done:
        should_task2_continue, data = task1.result()
        print("DATA", data)
        result1 = should_task2_continue # Store task1's result
        
        if not should_task2_continue:
            print("Condition met: Task 1 returned False. Cancelling Task 2.")
            for task in pending:
                task.cancel()
            # We must still await the cancelled task to finalize it
            try:
                await asyncio.gather(*pending)
            except asyncio.CancelledError:
                print("Main: Confirmed pending task was cancelled.")
        else:
            print("Condition not met: Task 1 returned True. Waiting for Task 2 to complete.")
            # await the remaining task (task2) and get its result
            pending_results = await asyncio.gather(*pending)
            result2 = pending_results[0] # Store task2's result

    # --- FINAL STEP: This block runs after the main logic is complete ---
    print("\n--- Final Processing Step ---")
    if result1 is not None and result2 is not None:
        # This branch only runs if task2 was allowed to complete
        print(f"✅ Both tasks returned successfully.")
        print(f"   - Result from Task 1: {result1}")
        print(f"   - Result from Task 2: {result2}")
        print("   -> Combining results now...")
    else:
        # This branch runs if task2 was cancelled
        print(f"❌ Process finished, but not all tasks returned a result.")
        print(f"   - Result from Task 1: {result1}")
        print(f"   - Result from Task 2: Was not obtained (cancelled).")

    print("--- Main orchestration finished ---")


if __name__ == "__main__":
    asyncio.run(main())