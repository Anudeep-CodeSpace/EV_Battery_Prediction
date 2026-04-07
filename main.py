def main():
    from dotenv import load_dotenv
    from app import app

    load_dotenv()

    app.run(debug=True)    


if __name__ == "__main__":
    main()
