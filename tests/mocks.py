"""Mock implementations for LLM and Embeddings for testing without API keys."""

from typing import Any, List, Optional, Type, Union, get_origin, get_args, Dict
from enum import Enum
from pydantic import BaseModel, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableSerializable, RunnableConfig


class MockEmbeddings(Embeddings):
    """Mock Embeddings that returns deterministic vectors based on str hash."""

    def __init__(self, dim: int = 768):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return deterministic embedding vectors based on text hash."""
        return [self._hash_to_vector(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Return deterministic embedding vector for query."""
        return self._hash_to_vector(text)

    def _hash_to_vector(self, text: str) -> List[float]:
        """Convert text to deterministic vector of given dimension."""
        hash_val = hash(text)
        return [(hash_val + i) % 1000 / 1000.0 for i in range(self.dim)]


class MockStructuredRunnable(RunnableSerializable):
    """
    Mock Runnable that simulates with_structured_output behavior.
    Generates dummy data matching the given Pydantic schema.
    """

    schema: Type[BaseModel]

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self, input: Any, config: Optional[RunnableConfig] = None
    ) -> BaseModel:
        """Generate and return a mock instance of the schema."""
        return self._generate_mock_instance(self.schema)

    def batch(
        self,
        inputs: List[Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[BaseModel]:
        """Generate mock instances for batch input."""
        return [self.invoke(inp, config) for inp in inputs]

    def _get_field_info(self, field_type: Type) -> tuple:
        """Get the base type and whether it's Optional."""
        origin = get_origin(field_type)

        if origin is Union:
            args = get_args(field_type)
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1 and type(None) in args:
                return non_none_args[0], True
            return field_type, False

        return field_type, False

    def _generate_mock_instance(self, model_cls: Type[BaseModel]) -> BaseModel:
        """Recursively generate mock instance matching schema."""
        data = {}

        for field_name, field_info in model_cls.model_fields.items():
            field_type = field_info.annotation

            origin = get_origin(field_type)
            is_optional = False

            if origin is Union:
                base_type, is_optional = self._get_field_info(field_type)
                field_type = base_type
                origin = get_origin(field_type)

            default = field_info.default
            has_default = (
                default is not None
                or field_info.default_factory is not None
            )

            if is_optional and not has_default:
                data[field_name] = None
                continue

            value = self._generate_value_for_type(field_type, origin, field_name)
            data[field_name] = value

        return model_cls(**data)

    def _generate_value_for_type(
        self, field_type: Type, origin: Any, field_name: str
    ) -> Any:
        """Generate a mock value for a given field type."""
        if origin is list:
            args = get_args(field_type)
            if args and issubclass(args[0], BaseModel):
                return [self._generate_mock_instance(args[0])]
            return []

        if origin is dict:
            args = get_args(field_type)
            key_type = args[0] if len(args) > 0 else str
            value_type = args[1] if len(args) > 1 else Any
            return {}

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            return list(field_type)[0] if len(field_type) > 0 else None

        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return self._generate_mock_instance(field_type)

        if field_type == str:
            return f"mock_{field_name}"
        elif field_type == int:
            return 1
        elif field_type == float:
            return 1.0
        elif field_type == bool:
            return True
        elif field_type == Any:
            return f"mock_{field_name}"
        else:
            return None


class MockChatModel(BaseChatModel):
    """Mock Chat Model for testing without API calls."""

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Generate mock response."""
        return type("ChatResult", (), {
            "generations": [
                type("Generation", (), {"message": AIMessage(content="mock response")})
            ]
        })()

    def with_structured_output(
        self, schema: Type[BaseModel], **kwargs: Any
    ) -> RunnableSerializable:
        """
        Return a MockStructuredRunnable that generates mock data matching the schema.
        This simulates LangChain's with_structured_output behavior.
        """
        runnable = MockStructuredRunnable(schema=schema)
        return runnable
