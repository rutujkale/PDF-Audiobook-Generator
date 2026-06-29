print("Main.py started")

from src.app import App


def main():
    print("Creating App...")
    app = App()
    print("Running App...")
    app.run()


if __name__ == "__main__":
    main()