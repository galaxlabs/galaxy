from galaxy.model.runtimemeta import RuntimeMeta
from galaxy.model.field_dependency_engine import evaluate_dependency


def build_dependency_graph(meta: RuntimeMeta) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for dep in meta.field_dependencies:
        if not dep.get("enabled", True):
            continue
        field_name = dep.get("field_name", "")
        depends_on = dep.get("depends_on_field", "")
        if field_name and depends_on:
            graph.setdefault(field_name, []).append(depends_on)
    return graph


def detect_cycles(meta: RuntimeMeta) -> list[list[str]]:
    graph = build_dependency_graph(meta)
    all_nodes = set(graph.keys()) | {d for deps in graph.values() for d in deps}
    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []
    parent: dict[str, str | None] = {}

    def dfs(node: str, path: list[str]):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                parent[neighbor] = node
                dfs(neighbor, path)
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
        path.pop()
        rec_stack.discard(node)

    for node in all_nodes:
        if node not in visited:
            dfs(node, [])
    return cycles


def topological_sort(meta: RuntimeMeta) -> list[str]:
    graph = build_dependency_graph(meta)
    all_fields = {d["field_name"] for d in meta.field_dependencies if d.get("enabled", True)}
    dependents = {d for deps in graph.values() for d in deps}
    all_nodes = all_fields | dependents
    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    for deps in graph.values():
        for d in deps:
            in_degree[d] = in_degree.get(d, 0) + 1
    queue = [n for n in all_nodes if in_degree.get(n, 0) == 0]
    result: list[str] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    remaining = [n for n in all_nodes if in_degree.get(n, 0) > 0]
    result.extend(remaining)
    return result


def resolve_chain_dependencies(meta: RuntimeMeta, doc_data: dict) -> dict[str, list[dict]]:
    cycles = detect_cycles(meta)
    if cycles:
        raise ValueError(f"Circular dependency detected: {cycles}")
    order = topological_sort(meta)
    dep_map: dict[str, list[dict]] = {}
    for dep in meta.field_dependencies:
        if not dep.get("enabled", True):
            continue
        fname = dep.get("field_name", "")
        if fname:
            dep_map.setdefault(fname, []).append(dep)
    results: dict[str, list[dict]] = {}
    for fname in order:
        if fname not in dep_map:
            continue
        for dep in dep_map[fname]:
            effective = evaluate_dependency(dep, doc_data)
            results.setdefault(fname, []).append({
                "action": dep.get("action", "show"),
                "effective": effective,
                "depends_on_field": dep.get("depends_on_field", ""),
                "depends_on_value": dep.get("depends_on_value", ""),
                "chain_order": order.index(fname),
            })
    for fname, deps in dep_map.items():
        if fname not in results:
            for dep in deps:
                if dep.get("condition"):
                    effective = evaluate_dependency(dep, doc_data)
                else:
                    effective = True
                results.setdefault(fname, []).append({
                    "action": dep.get("action", "show"),
                    "effective": effective,
                    "depends_on_field": dep.get("depends_on_field", ""),
                    "depends_on_value": dep.get("depends_on_value", ""),
                })
    return results


def get_chain_field_states(meta: RuntimeMeta, doc_data: dict) -> dict[str, dict]:
    try:
        deps = resolve_chain_dependencies(meta, doc_data)
    except ValueError:
        deps = {}
    from galaxy.model.field_dependency_engine import get_effective_field_states as basic_states
    base = basic_states(meta, doc_data)
    for fname, entries in deps.items():
        for entry in entries:
            if entry["action"] == "hide":
                base.setdefault(fname, {})["hidden"] = entry["effective"]
            elif entry["action"] == "show":
                base.setdefault(fname, {})["hidden"] = not entry["effective"]
            elif entry["action"] == "require":
                base.setdefault(fname, {})["required"] = entry["effective"]
            elif entry["action"] == "readonly":
                base.setdefault(fname, {})["read_only"] = entry["effective"]
    return base


__all__ = [
    "build_dependency_graph", "detect_cycles", "topological_sort",
    "resolve_chain_dependencies", "get_chain_field_states",
]
