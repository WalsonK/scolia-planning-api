from libs.rustml_wrapper import Rustml 
import basic_function as fn

if __name__ == "__main__":
    # Initialize the Rustml wrapper
    rustml = Rustml()

    # Example usage of the Rustml wrapper
    result = rustml.add(5, 3)
    print(f"Result from Rust: {result}")

    # data = fn.load_data()
    # print(f"Data loaded: {data}")

    test = rustml.generate_greedy_planning(
        total_slots=7,
        max_hours=35,
        slot_minutes=90,
        subjects=[0.0],
        todo=[8.0],
        unavailability=[[1.0]]
    )
    print(f"Test result: {test}")