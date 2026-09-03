"""Extraction prompt parser from guideline."""

LABEL_MAPPING = {
    "zh": {
        "role_and_task": "角色与任务",
        "known_entities": "已知实体",
        "rules": "提取规则",
        "entity_rules": "实体提取规则",
        "relation_rules": "关系提取规则",
        "time_rules": "时间规则",
        "location_rules": "位置规则",
        "source_text": "源文本",
    },
    "en": {
        "role_and_task": "Role and Task",
        "known_entities": "Known Entities",
        "rules": "Extraction Rules",
        "entity_rules": "Entity Extraction Rules",
        "relation_rules": "Relation Extraction Rules",
        "time_rules": "Time Rules",
        "location_rules": "Location Rules",
        "source_text": "Source Text",
    },
}


def parse_guideline(
    guideline, autotype: str, language: str = "en"
) -> str | tuple[str, str, str]:
    """Parse guideline and return prompts based on autotype (config is already localized).

    Args:
        guideline: Guideline instance (single-language, all fields are strings)
        autotype: Template type (default: "model")
        language: Language for the section labels (falls back to "en").

    Returns:
        tuple: main_prompt or (main_prompt, node_prompt, edge_prompt)
        - For non-graph types: returns main_prompt
        - For graph types in two_stage mode: returns (main_prompt, node_prompt, edge_prompt)
    """
    labels = LABEL_MAPPING.get(language, LABEL_MAPPING["en"])

    prefix_prompt = f"# {labels.get('role_and_task')}:\n{guideline.target}"

    if autotype in ("model", "list", "set"):
        parts = [prefix_prompt]
        if guideline.rules:
            parts.append(f"## {labels.get('rules')}:\n{guideline.rules}")
        parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")
        return "\n\n".join(parts)
    else:
        main_parts = [prefix_prompt]
        if guideline.rules_for_entities:
            main_parts.append(
                f"## {labels.get('entity_rules')}:\n{guideline.rules_for_entities}"
            )
        if guideline.rules_for_relations:
            main_parts.append(
                f"## {labels.get('relation_rules')}:\n{guideline.rules_for_relations}"
            )
        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            if guideline.rules_for_time:
                main_parts.append(
                    f"## {labels.get('time_rules')}:\n{guideline.rules_for_time}"
                )
        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            if guideline.rules_for_location:
                main_parts.append(
                    f"## {labels.get('location_rules')}:\n{guideline.rules_for_location}"
                )
        main_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        node_parts = [prefix_prompt]
        if guideline.rules_for_entities:
            node_parts.append(
                f"## {labels.get('entity_rules')}:\n{guideline.rules_for_entities}"
            )
        node_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        edge_parts = [prefix_prompt]
        if guideline.rules_for_relations:
            edge_parts.append(
                f"## {labels.get('relation_rules')}:\n{guideline.rules_for_relations}"
            )
        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            if guideline.rules_for_time:
                edge_parts.append(
                    f"## {labels.get('time_rules')}:\n{guideline.rules_for_time}"
                )
        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            if guideline.rules_for_location:
                edge_parts.append(
                    f"## {labels.get('location_rules')}:\n{guideline.rules_for_location}"
                )
        edge_parts.append(f"## {labels.get('known_entities')}:\n{{known_nodes}}")
        edge_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        return "\n\n".join(main_parts), "\n\n".join(node_parts), "\n\n".join(edge_parts)


__all__ = [
    "parse_guideline",
]
