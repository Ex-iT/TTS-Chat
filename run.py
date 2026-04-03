from app import create_app
from app.config import config

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.PORT, debug=True)
