from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_PAT: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_ID: str = "llama3.1:8b"

    # LangSmith / OpenTelemetry Tracing
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com/otel/v1/traces"
    LANGSMITH_PROJECT: str = "sdk"

    # AWS Serverless / SAM CLI Configuration
    AWS_SERVERLESS_MCP_COMMAND: str = "uvx"
    AWS_SERVERLESS_MCP_ARGS: list[str] = ["awslabs.aws-serverless-mcp-server@latest"]
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_SESSION_TOKEN: str = ""
    AWS_REGION: str = "us-east-1"
    
    # AWS Bedrock Configuration
    BEDROCK_MODEL_ID: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    # S3 Session Memory Configuration
    AWS_S3_SESSION_BUCKET_NAME: str = ""
    AWS_S3_SESSION_PREFIX: str = "sessions"

    # Bedrock Knowledge Base Configuration
    BEDROCK_KNOWLEDGE_BASE_ID: str = ""
    BEDROCK_KB_DATA_SOURCE_ID: str = ""

    # Text Editor MCP Configuration
    TEXT_EDITOR_MCP_COMMAND: str = "uvx"
    TEXT_EDITOR_MCP_ARGS: list[str] = ["mcp-text-editor"]

    # Groq Model Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL_ID: str = "qwen/qwen3.8-27b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
