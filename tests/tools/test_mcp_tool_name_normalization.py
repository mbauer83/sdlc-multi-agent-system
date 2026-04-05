from __future__ import annotations

from src.tools.mcp_model_server import _normalize_incoming_tool_name as norm_model
from src.tools.mcp_registry_server import _normalize_incoming_tool_name as norm_registry


def test_normalize_incoming_tool_name_keeps_known() -> None:
    known = {"list_agents"}
    assert norm_registry("list_agents", known_tools=known) == "list_agents"


def test_normalize_incoming_tool_name_strips_prefix_hyphen() -> None:
    known = {"list_agents"}
    assert norm_registry("AgentsAndSkills-list_agents", known_tools=known) == "list_agents"


def test_normalize_incoming_tool_name_strips_prefix_other_separators() -> None:
    known = {"model_query_stats"}
    assert norm_model("ModelTools:model_query_stats", known_tools=known) == "model_query_stats"
    assert norm_model("ModelTools.model_query_stats", known_tools=known) == "model_query_stats"
    assert norm_model("ModelTools/model_query_stats", known_tools=known) == "model_query_stats"


def test_normalize_incoming_tool_name_unknown_passthrough() -> None:
    known = {"list_agents"}
    assert norm_registry("AgentsAndSkills-not_a_real_tool", known_tools=known) == "AgentsAndSkills-not_a_real_tool"
