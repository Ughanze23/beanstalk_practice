from website import create_app

application = create_app()  # Move this outside of the `if __name__ == "__main__"` block

if __name__ == "__main__":
    application.run(debug=True)
