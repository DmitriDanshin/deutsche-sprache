from app.app import App

if __name__ == '__main__':
    app = App(
        verbformen_query={"w": "Hund"},
        context_reverso_query={"w": "Hund"}
    )
    app.run()
