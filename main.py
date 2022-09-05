from app.app import App

if __name__ == '__main__':
    app = App(
        verbformen_query={"w": "Hund"},
        wikionary_query={"w": "Hund", "lang": "ru"}
    )
    app.run()
