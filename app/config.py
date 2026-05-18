from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ERP-FSM"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/erp_fsm"

    model_config = {"env_file": ".env"}


settings = Settings()
