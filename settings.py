from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Kancelaria AI – MVP"
    VERSION: str = "1.0.0"
    # OPENAI_API_KEY opcjonalnie później
    # OPENAI_MODEL: str = "gpt-4o-mini"

settings = Settings()
