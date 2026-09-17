from pydantic import BaseSettings



class Settings(BaseSettings):
    GITHUB_PAT: str
    