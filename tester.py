from libs.rustml_wrapper import Rustml 
import basic_function as fn

if __name__ == "__main__":
    # Initialize the Rustml wrapper
    rustml = Rustml()

    # Example usage of the Rustml wrapper
    result = rustml.add(5, 3)
    print(f"Result from Rust: {result}")

    data = fn.load_data()
    print(f"Data loaded: {data}")