from .name_normalization import install_call_tool_normalizer, normalize_incoming_tool_name
from .register_tools import register_framework_query_tools

__all__ = [
    "install_call_tool_normalizer",
    "normalize_incoming_tool_name",
    "register_framework_query_tools",
]
