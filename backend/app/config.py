"""
Global Configuration and Debug Settings
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings with debug configuration"""
    
    # ============================================================================
    # AWS Configuration
    # ============================================================================
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_profile: Optional[str] = None
    s3_bucket: str = "mediquery-documents"
    opensearch_endpoint: str = ""
    opensearch_username: str = "admin"
    opensearch_password: str = "Admin123!"
    bedrock_model_id: str = Field(
        default="anthropic.claude-sonnet-4-5-20250514-v1:0",
        description="Bedrock model ID for Claude Sonnet 4.5"
    )
    
    # Anthropic Direct API (Temporary fallback while AWS Marketplace resolves)
    use_direct_anthropic: bool = Field(
        default=False,
        description="Use Anthropic API directly instead of Bedrock (temporary)"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for direct access"
    )
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model name for direct API"
    )
    
    # ChromaDB (Alternative vector database for testing)
    use_chromadb: bool = Field(
        default=False,
        description="Use ChromaDB instead of OpenSearch for vector storage"
    )
    chromadb_persist_directory: str = Field(
        default="./chroma_data",
        description="Directory to persist ChromaDB data"
    )
    
    # ============================================================================
    # Application Configuration
    # ============================================================================
    app_name: str = "MediQuery AI"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    max_file_size: int = 52428800  # 50MB
    allowed_file_types: list[str] = [".pdf"]
    
    # ============================================================================
    # Document Processing
    # ============================================================================
    chunk_size: int = 512  # tokens
    chunk_overlap: int = 50  # tokens
    max_chunks_per_document: int = 1000
    
    # ============================================================================
    # Vector Search Configuration
    # ============================================================================
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_dimension: int = 1024
    embedding_batch_size: int = 32
    top_k_retrieval: int = 20
    top_k_rerank: int = 5
    
    # ============================================================================
    # LLM Configuration
    # ============================================================================
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.1
    llm_top_p: float = 0.9
    
    # ============================================================================
    # DEBUG CONFIGURATION
    # ============================================================================
    
    # Global Debug Mode
    debug_mode: bool = True  # Set to False in production
    
    # Logging Configuration
    log_level: LogLevel = LogLevel.DEBUG
    log_format: str = "console"  # "json" or "console"
    log_to_file: bool = True
    log_file_path: str = "logs/mediquery.log"
    log_rotation: str = "100 MB"
    log_retention: str = "30 days"
    
    # Agent Tracing
    trace_agents: bool = True
    trace_agent_inputs: bool = True
    trace_agent_outputs: bool = True
    trace_agent_timing: bool = True
    trace_agent_state: bool = False  # Can be verbose
    
    # LLM Tracing
    trace_llm_calls: bool = True
    trace_llm_prompts: bool = True
    trace_llm_responses: bool = True
    trace_llm_tokens: bool = True
    trace_llm_cost: bool = True
    
    # Performance Monitoring
    enable_performance_metrics: bool = True
    slow_query_threshold_ms: int = 3000
    slow_agent_threshold_ms: int = 1000
    
    # Distributed Tracing
    enable_xray: bool = False  # Enable in AWS
    enable_opentelemetry: bool = False  # Enable for advanced tracing
    
    # Debug Output
    print_agent_trace: bool = True  # Console output
    save_trace_to_response: bool = True  # Include in API response
    
    # Error Handling
    verbose_errors: bool = True  # Detailed error messages in debug mode
    include_stack_trace: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Debug configuration helper
class DebugConfig:
    """Helper class for debug configuration"""
    
    @staticmethod
    def is_debug_mode() -> bool:
        """Check if debug mode is enabled"""
        return settings.debug_mode
    
    @staticmethod
    def should_trace_agents() -> bool:
        """Check if agent tracing is enabled"""
        return settings.trace_agents
    
    @staticmethod
    def should_trace_llm() -> bool:
        """Check if LLM tracing is enabled"""
        return settings.trace_llm_calls
    
    @staticmethod
    def get_log_level() -> str:
        """Get current log level"""
        return settings.log_level.value
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production mode"""
        return not settings.debug_mode


debug_config = DebugConfig()
