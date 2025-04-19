from libs.rustml_wrapper import Rustml 

if __name__ == "__main__":
    # Initialize the Rustml wrapper
    rustml = Rustml()

    # Example usage of the Rustml wrapper
    result = rustml.add(5, 3)
    print(f"Result from Rust: {result}")