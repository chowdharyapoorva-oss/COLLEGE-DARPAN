import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Keep local development usable without a checked-in, predictable signing key.
    # Set SECRET_KEY in the environment when sessions must survive app restarts.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE_PATH = os.environ.get(
        "COLLEGE_DARPAN_DATABASE_PATH",
        os.path.join(BASE_DIR, "database", "college_darpan.db"),
    )
    DEBUG = os.environ.get("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes", "on"}
    
    # Default recommendation weights (normalized)
    DEFAULT_WEIGHTS = {
        "branch": 0.30,
        "affordability": 0.25,
        "placements": 0.20,
        "location": 0.10,
        "infrastructure": 0.15,
    }
    
    # Platform metadata
    PLATFORM_NAME = "College Darpan"
    TAGLINE = "Your Future. Your College. Your Choice."
    STATE = "Telangana"
