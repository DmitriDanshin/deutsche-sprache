from app.app import App

if __name__ == '__main__':
    app = App(
        verbformen_query={"w": "heiss"}
    )
    app.run()
