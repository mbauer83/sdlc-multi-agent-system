from __future__ import annotations

import math
import re

from src.common.domain_vocabulary import expand_tokens
from src.common.model_query_types import ConnectionRecord, DiagramRecord, EntityRecord


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def token_match_score(field_text: str, query_lc: str, tokens: list[str], weight: float) -> float:
    if not field_text:
        return 0.0
    field_lc = field_text.lower()
    score = weight if query_lc in field_lc else 0.0
    for token in tokens:
        if token in field_lc:
            score += weight * 0.5
    return score


def content_score(content: str, tokens: list[str], weight: float) -> float:
    if not content or not tokens:
        return 0.0
    content_lc = content.lower()
    word_count = max(len(content_lc.split()), 1)
    tf_sum = 0.0
    for token in tokens:
        count = content_lc.count(token)
        if count:
            tf = count / word_count
            tf_sum += weight * (1 + math.log(1 + tf))
    return tf_sum


def score_entity(rec: EntityRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = expand_tokens(tokens)
    score = 0.0
    score += token_match_score(rec.name, query_lc, expanded, 4.0)
    score += token_match_score(rec.display_label, query_lc, expanded, 3.5)
    score += token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += token_match_score(rec.display_alias, query_lc, expanded, 2.0)
    score += token_match_score(rec.artifact_type, query_lc, expanded, 2.0)
    score += token_match_score(rec.layer, query_lc, expanded, 1.5)
    score += token_match_score(rec.sublayer, query_lc, expanded, 1.5)
    score += token_match_score(rec.owner_agent, query_lc, expanded, 1.0)
    score += token_match_score(rec.phase_produced, query_lc, expanded, 1.0)
    score += content_score(rec.content_text, expanded, 1.0)
    for value in rec.extra.values():
        score += token_match_score(str(value), query_lc, expanded, 0.5)
    return score


def score_connection(rec: ConnectionRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = expand_tokens(tokens)
    score = 0.0
    score += token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += token_match_score(rec.artifact_type, query_lc, expanded, 2.0)
    score += token_match_score(rec.conn_lang, query_lc, expanded, 1.5)
    score += token_match_score(rec.conn_type, query_lc, expanded, 1.5)
    for entity_id in rec.source_ids + rec.target_ids:
        score += token_match_score(entity_id, query_lc, expanded, 1.5)
    score += content_score(rec.content_text, expanded, 1.0)
    return score


def score_diagram(rec: DiagramRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = expand_tokens(tokens)
    score = 0.0
    score += token_match_score(rec.name, query_lc, expanded, 4.0)
    score += token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += token_match_score(rec.diagram_type, query_lc, expanded, 2.0)
    score += token_match_score(rec.owner_agent, query_lc, expanded, 1.0)
    score += token_match_score(rec.phase_produced, query_lc, expanded, 1.0)
    return score
