from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_PAT: str
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL_ID: str

    # LangSmith / OpenTelemetry Tracing
    LANGSMITH_TRACING: bool 
    LANGSMITH_API_KEY: str 
    LANGSMITH_ENDPOINT: str 
    LANGSMITH_PROJECT: str 

    # AWS Serverless / SAM CLI Configuration
    AWS_SERVERLESS_MCP_COMMAND: str 
    AWS_SERVERLESS_MCP_ARGS: list[str] =["awslabs.aws-serverless-mcp-server@latest"]
    AWS_ACCESS_KEY_ID: str  
    AWS_SECRET_ACCESS_KEY: str 
    AWS_SESSION_TOKEN: str 
    AWS_REGION: str 
    
    # AWS Bedrock Configuration
    BEDROCK_MODEL_ID: str 

    # S3 Session Memory Configuration
    AWS_S3_SESSION_BUCKET_NAME: str 
    AWS_S3_SESSION_PREFIX: str

    # Bedrock Knowledge Base Configuration
    BEDROCK_KNOWLEDGE_BASE_ID: str
    BEDROCK_KB_DATA_SOURCE_ID: str

    # Text Editor MCP Configuration
    TEXT_EDITOR_MCP_COMMAND: str = "uvx"
    TEXT_EDITOR_MCP_ARGS: list[str] = ["mcp-text-editor"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
