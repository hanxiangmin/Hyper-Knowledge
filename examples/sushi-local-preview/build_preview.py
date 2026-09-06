"""Build the source-grounded Su Shi local preview without an extraction provider.

The declarations below are editorial candidate assertions, not graph algorithms.
The source is copied byte-for-byte; quotes are verified against their literal spans.
Run from any directory using the repository-managed Python environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from hyperknowledge.bundle import validate_bundle


ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / "sushi-document-test"
SOURCE_SHA256 = "65869e3042b4a3b7a83695f1a053f8a2d99a09d031167770d4636e433442c0ed"
SOURCE_PATH = "source/sushi.md"


# role -> canonical entity. Repeated role labels are valid for distinct members.
# The short assertion ID is an explicit, context-specific instance ID, not a label.
RELATIONS = [
    {
        "id": "family-san-su",
        "name": "三苏",
        "semantics": "family_literary_group",
        "theme": "家学与文学群体",
        "lines": [(3, 3)],
        "members": [
            ("person:su-shi", "核心人物"),
            ("person:su-xun", "父亲"),
            ("person:su-zhe", "弟弟"),
            ("group:san-su", "群体称谓"),
        ],
    },
    {
        "id": "san-su-tang-song-membership",
        "name": "同列唐宋八大家",
        "semantics": "source_explicit_joint_group_membership",
        "theme": "家学与文学群体",
        "lines": [(3, 3)],
        "members": [
            ("person:su-shi", "作家"),
            ("person:su-xun", "作家"),
            ("person:su-zhe", "作家"),
            ("group:tang-song-eight", "文学群体"),
        ],
    },
    {
        "id": "imperial-exam-1057",
        "name": "科举考试",
        "semantics": "examination_event",
        "theme": "仕履与政见",
        "year": 1057,
        "lines": [(13, 15)],
        "members": [
            ("person:su-shi", "考生"),
            ("person:su-zhe", "同科考生"),
            ("person:ouyang-xiu", "主考官"),
            ("person:zeng-gong", "被误认作者"),
            ("time:1057", "考试年份"),
        ],
    },
    {
        "id": "new-policies-conflict",
        "name": "新法政见分歧",
        "semantics": "political_reform_conflict",
        "theme": "仕履与政见",
        "lines": [(19, 19)],
        "properties": {
            "time_binding": "background_accession_year_not_conflict_date",
            "summary": "1067年是该段明确写出的即位背景年份，不据此断定所有新法争论发生于该年。",
        },
        "members": [
            ("person:su-shi", "批评者"),
            ("person:wang-anshi", "变法主持者"),
            ("person:song-shenzong", "新法时期君主"),
            ("policy:new-policies", "争议政策"),
            ("time:1067", "即位背景年份"),
        ],
    },
    {
        "id": "wutai-poetry-case",
        "name": "乌台诗案",
        "semantics": "judicial_case_event",
        "theme": "黄州经历",
        "year": 1079,
        "lines": [(25, 25), (27, 27)],
        "members": [
            ("person:su-shi", "被指控者"),
            ("person:li-ding", "指控者"),
            ("person:shu-dan", "指控者"),
            ("person:su-zhe", "求情者"),
            ("person:wang-shen", "营救者"),
            ("place:yushitai-prison", "拘押地点"),
            ("time:1079", "案件年份"),
            ("policy:new-policies", "诗作批评对象"),
        ],
    },
    {
        "id": "huangzhou-arrival-1080",
        "name": "抵达黄州",
        "semantics": "biographical_relocation_event",
        "theme": "黄州经历",
        "year": 1080,
        "lines": [(29, 29), (33, 33)],
        "properties": {
            "narrative_predecessor": "assertion:wutai-poetry-case",
            "summary": "原文先叙述乌台诗案后被贬黄州，再明确记载1080年抵达；不生成因果二元边。",
        },
        "members": [
            ("person:su-shi", "到达者"),
            ("time:1080", "到达年份"),
            ("place:huangzhou", "到达地点"),
        ],
    },
    {
        "id": "huangzhou-literary-works",
        "name": "黄州创作",
        "semantics": "place_bound_literary_creation",
        "theme": "黄州经历",
        "lines": [(35, 35)],
        "properties": {
            "time_binding": "undated_huangzhou_period",
            "summary": "这些作品与黄州创作时期的关系由原文明确陈述；没有把1082年当作整个阶段的结束年份。",
        },
        "members": [
            ("person:su-shi", "创作者"),
            ("place:huangzhou", "创作地点"),
            ("work:nian-nu-jiao", "作品"),
            ("work:qian-chibi-fu", "作品"),
            ("work:ding-feng-bo", "作品"),
        ],
    },
    {
        "id": "huangzhou-foyin-friendship",
        "name": "黄州交游",
        "semantics": "place_bound_friendship",
        "theme": "黄州经历",
        "lines": [(37, 37)],
        "members": [
            ("person:su-shi", "友人"),
            ("person:foyin", "友人"),
            ("place:huangzhou", "交游地点"),
        ],
    },
    {
        "id": "hangzhou-appointment-1071",
        "name": "任杭州通判",
        "semantics": "public_office_appointment",
        "theme": "杭州任职与治理",
        "year": 1071,
        "lines": [(21, 21)],
        "properties": {"office": "杭州通判", "term_index": 1},
        "members": [
            ("person:su-shi", "任职者"),
            ("time:1071", "任职年份"),
            ("place:hangzhou", "任职地点"),
        ],
    },
    {
        "id": "west-lake-governance-1089",
        "name": "治理西湖",
        "semantics": "place_bound_public_works",
        "theme": "杭州任职与治理",
        "year": 1089,
        "lines": [(41, 41), (72, 72)],
        "properties": {"office": "杭州知州", "term_index": 2},
        "members": [
            ("person:su-shi", "治理者"),
            ("place:hangzhou", "任职地点"),
            ("place:west-lake", "治理对象"),
            ("infrastructure:su-causeway", "修筑工程"),
            ("time:1089", "任职与修堤年份"),
        ],
    },
    {
        "id": "anlefang-founding-hangzhou",
        "name": "创立安乐坊",
        "semantics": "institution_founding",
        "theme": "杭州任职与治理",
        "lines": [(43, 43)],
        "properties": {"time_binding": "not_specified_in_source_sentence"},
        "members": [
            ("person:su-shi", "创立者"),
            ("place:hangzhou", "设立地点"),
            ("institution:anlefang", "创立机构"),
        ],
    },
    {
        "id": "huizhou-exile-1094",
        "name": "贬谪惠州",
        "semantics": "biographical_relocation_event",
        "theme": "晚年贬谪与北归",
        "year": 1094,
        "lines": [(51, 51)],
        "properties": {"trajectory_index": 1},
        "members": [
            ("person:su-shi", "被贬者"),
            ("time:1094", "贬谪年份"),
            ("place:huizhou", "贬谪地点"),
        ],
    },
    {
        "id": "danzhou-exile-1097",
        "name": "贬谪儋州",
        "semantics": "biographical_relocation_event",
        "theme": "晚年贬谪与北归",
        "year": 1097,
        "lines": [(51, 51)],
        "properties": {"trajectory_index": 2},
        "members": [
            ("person:su-shi", "被贬者"),
            ("time:1097", "贬谪年份"),
            ("place:danzhou", "贬谪地点"),
        ],
    },
    {
        "id": "changzhou-return-1101",
        "name": "北归",
        "semantics": "biographical_return_event",
        "theme": "晚年贬谪与北归",
        "year": 1101,
        "lines": [(55, 55)],
        "properties": {"trajectory_index": 3},
        "members": [
            ("person:su-shi", "北归者"),
            ("time:1101", "北归年份"),
            ("place:changzhou", "到达地点"),
        ],
    },
    {
        "id": "su-huang-poetry-name",
        "name": "苏黄并称",
        "semantics": "poetry_joint_appellation",
        "theme": "文学与书法",
        "lines": [(59, 59)],
        "members": [
            ("person:su-shi", "并称诗人"),
            ("person:huang-tingjian", "并称诗人"),
        ],
    },
    {
        "id": "su-xin-ci-name",
        "name": "苏辛并称",
        "semantics": "ci_joint_appellation",
        "theme": "文学与书法",
        "lines": [(59, 59)],
        "members": [
            ("person:su-shi", "并称词人"),
            ("person:xin-qiji", "并称词人"),
        ],
    },
    {
        "id": "su-shi-song-four-membership",
        "name": "宋四家之首",
        "semantics": "calligraphy_group_membership",
        "theme": "文学与书法",
        "lines": [(59, 59)],
        "members": [
            ("person:su-shi", "书家"),
            ("group:song-four", "书法群体"),
        ],
    },
    {
        "id": "cold-food-calligraphy-authorship",
        "name": "寒食帖作者",
        "semantics": "calligraphy_authorship",
        "theme": "文学与书法",
        "lines": [(59, 59)],
        "members": [
            ("person:su-shi", "作者"),
            ("work:huangzhou-cold-food", "书法作品"),
        ],
    },
]


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def table_bytes(rows: list[dict]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    ).encode("utf-8")


def build(*, force: bool = False) -> dict:
    source_bytes = (ORIGINAL / SOURCE_PATH).read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError(
            "Original source changed; review every source span before rebuilding."
        )
    lines = source_bytes.decode("utf-8").splitlines()
    nodes = [
        json.loads(line)
        for line in (ORIGINAL / "bundle/nodes.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    nodes = [node for node in nodes if node["id"] != "time:1080-1082"]
    nodes.extend(
        {
            "id": f"time:{year}",
            "label": f"{year}年",
            "type": "time",
            "properties": {"year": year, "source_lines": source_lines},
        }
        for year, source_lines in [(1071, [21, 68]), (1080, [33, 70])]
    )
    # Preserve supported two-member assertions in the same role-aware hypergraph.
    # Member count alone neither selects topology nor warrants a separate view.
    selected_node_ids = {
        node_id for relation in RELATIONS for node_id, _ in relation["members"]
    }
    nodes = [node for node in nodes if node["id"] in selected_node_ids]
    nodes.sort(key=lambda row: row["id"])
    node_ids = {node["id"] for node in nodes}
    members, assertions, evidence = [], [], []
    for relation in RELATIONS:
        assertion_id = "assertion:" + relation["id"]
        if len({node_id for node_id, _ in relation["members"]}) < 2:
            raise ValueError(
                f"This preview requires at least two distinct members: {assertion_id}"
            )
        refs = []
        for index, (start, end) in enumerate(relation["lines"], 1):
            evidence_id = f"evidence:{relation['id']}:{index}"
            # A full literal line range, including its internal blank lines.
            quote = "\n".join(lines[start - 1 : end])
            if not quote:
                raise ValueError(f"Empty source span for {assertion_id}")
            evidence.append(
                {
                    "id": evidence_id,
                    "type": "source_text_span",
                    "source": SOURCE_PATH,
                    "source_sha256": source_hash,
                    "line_start": start,
                    "line_end": end,
                    "support": "source_text_claim",
                    "quote": quote,
                }
            )
            refs.append(evidence_id)
        properties = {
            "construction_method": "editorial_source_mapping",
            "review_status": "pending_human_review",
            "remote_provider": False,
            "source_claim_only": True,
            "theme": relation["theme"],
            **relation.get("properties", {}),
        }
        if "year" in relation:
            properties["event_year"] = relation["year"]
        if "trajectory_index" in properties:
            properties["trajectory"] = relation["theme"]
        role_nodes = sorted(relation["members"])
        # A full member/role/context fingerprint makes semantic edits auditable.
        # Semantic instances retain explicit IDs; predicates are never merge keys.
        signature = {
            "semantics": relation["semantics"],
            "members": role_nodes,
            "context": properties,
        }
        properties["semantic_sha256"] = hashlib.sha256(
            json_text(signature).encode()
        ).hexdigest()
        assertions.append(
            {
                "id": assertion_id,
                "predicate": relation["name"],
                "semantics": relation["semantics"],
                "topology": "hyperedge",
                "epistemic_status": "editorial_candidate",
                "evidence_refs": refs,
                "properties": properties,
            }
        )
        for ordinal, (node_id, role) in enumerate(relation["members"]):
            if node_id not in node_ids:
                raise ValueError(f"Unresolved member: {node_id}")
            members.append(
                {
                    "assertion_id": assertion_id,
                    "node_id": node_id,
                    "role": role,
                    "ordinal": ordinal,
                    "resolved": True,
                }
            )
    # Importance and sharing count distinct incident assertions, not role rows.
    degree = Counter(
        node_id
        for _, node_id in {
            (member["assertion_id"], member["node_id"]) for member in members
        }
    )
    if set(degree) != node_ids:
        raise ValueError(f"Unreferenced entities: {node_ids - set(degree)}")
    assertions.sort(key=lambda row: row["id"])
    members.sort(key=lambda row: (row["assertion_id"], row["ordinal"]))
    evidence.sort(key=lambda row: row["id"])
    tables = {
        "nodes.jsonl": nodes,
        "assertions.jsonl": assertions,
        "members.jsonl": members,
        "evidence.jsonl": evidence,
    }
    encoded = {name: table_bytes(rows) for name, rows in tables.items()}
    counts = {
        "nodes": len(nodes),
        "assertions": len(assertions),
        "members": len(members),
        "unresolved_members": 0,
        "assertions_with_evidence": len(assertions),
    }
    manifest = {
        "schema_version": "hk.bundle/v1",
        "bundle_id": "bundle_sushi_local_preview_v1",
        "source_ka": None,
        "source_data_sha256": source_hash,
        "template": "editorial/biography-role-aware-local-preview-v1",
        "language": "zh",
        "topology_type": "hypergraph",
        "presentation": {
            "contour_layout": "single_hyperedge",
            "overview_layout": "radial_hypergraph",
        },
        "counts": counts,
        "sources": [
            {
                "path": SOURCE_PATH,
                "sha256": source_hash,
                "size_bytes": len(source_bytes),
            }
        ],
        "table_sha256": {
            name: hashlib.sha256(content).hexdigest()
            for name, content in encoded.items()
        },
        "build": {
            "script": "build_preview.py",
            "deterministic": True,
            "original_example": "../sushi-document-test",
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "modeling": {
            "hyperedges": sum(row["topology"] == "hyperedge" for row in assertions),
            "native_pairwise": sum(row["topology"] == "pairwise" for row in assertions),
            "shared_nodes": {
                node_id: n for node_id, n in sorted(degree.items()) if n > 1
            },
            "no_composite_stage_nodes": True,
        },
        "limitations": [
            "This is a source-grounded role-aware showcase bundle for demonstrating higher-order relation modeling.",
            "The source is a user-provided secondary biography. Claims are not independently historically fact-checked.",
            "Relations are explicitly declared knowledge-pack editorial candidates, not an extraction run or human-confirmed facts; literal spans prove source presence, not historical truth.",
            "The 1067 member is an accession background year, not an exact date of every new-policy disagreement.",
            "The Huangzhou creation period and Anlefang founding have no invented exact endpoint/year.",
            "Two-member assertions remain hyperedges in this role-aware bundle, without a separate pairwise view; no third member is invented and unrelated assertions are not merged.",
        ],
    }
    report = (
        "# 苏轼：角色与共享结构本地预览\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in counts.items())
        + "\n\n"
        + (
            "保留原始独立实体名称；删除无依据的 1080—1082 年阶段，补入明确的 1071 年、1080 年。\n"
            "本预览保留 18 条无向超边，含 4 条双成员超边；统一展示超边，不为凑数增添成员或单独增加二元关系视图。\n"
            "关系由显式声明的知识包候选记录生成，尚待人工审阅；未调用抽取模型，也不标为人工确认。\n"
            "每条证据引用均是原文指定行范围的逐字内容，事实本身仍需独立历史核验。\n"
            "详见上一级 README.md 的逐条建模变化与来源。\n"
        )
    )
    files = {
        ROOT / SOURCE_PATH: source_bytes,
        ROOT / "bundle/manifest.json": json_text(manifest).encode(),
        ROOT / "bundle/REPORT.md": report.encode(),
        **{ROOT / "bundle" / name: content for name, content in encoded.items()},
    }
    for path, content in files.items():
        if path.exists() and path.read_bytes() != content and not force:
            raise FileExistsError(
                f"Existing generated content differs: {path}; review then use --force."
            )
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    receipt = validate_bundle(ROOT / "bundle", quality="showcase")
    receipt["bundle"] = "examples/sushi-local-preview/bundle"
    (ROOT / "validation.json").write_text(json_text(receipt), encoding="utf-8")
    failures = receipt.get("diagnostics", [])
    if receipt.get("status") == "failed":
        raise ValueError(json_text(failures))
    summary = {
        "bundle": "examples/sushi-local-preview/bundle",
        "status": receipt["status"],
        **counts,
        "checks": len(receipt.get("checks", [])),
        "diagnostics": failures,
        **manifest["modeling"],
        "source_sha256": source_hash,
    }
    print(json_text(summary))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace only this preview's deterministic generated files.",
    )
    build(force=parser.parse_args().force)
