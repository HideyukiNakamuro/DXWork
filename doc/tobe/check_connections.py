import json

SUMMARY_FILE = 'summary.json'

with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
    summary = json.load(f)

# サブグラフごとにノード名・nameを辞書化
graph_nodes = {}
for group in summary:
    subgraph = group['subgraph']
    nodes = set()
    for node in group['nodes']:
        if node.get('node'):
            nodes.add(str(node['node']))
        if node.get('name'):
            nodes.add(str(node['name']))
    graph_nodes[subgraph] = nodes

problems = []
for group in summary:
    this_subgraph = group['subgraph']
    for node in group['nodes']:
        froms = node.get('from', [])
        # from配列がなければ従来の単体from_subgraph/from_nodeも見る（後方互換）
        if not froms and (node.get('from_subgraph') or node.get('from_node')):
            froms = [{
                'from_subgraph': node.get('from_subgraph', ''),
                'from_node': node.get('from_node', '')
            }]
        for f in froms:
            fs = f.get('from_subgraph', '')
            fn = f.get('from_node', '')
            if fs and fn:
                if fs not in graph_nodes:
                    problems.append(f"サブグラフ '{this_subgraph}' のノード '{node.get('node','')}' のfrom_subgraph '{fs}' が存在しません")
                elif fn not in graph_nodes[fs]:
                    problems.append(f"サブグラフ '{this_subgraph}' のノード '{node.get('node','')}' のfrom_node '{fn}' はサブグラフ '{fs}' に存在しません")

if problems:
    print('接続関係に問題があります:')
    for p in problems:
        print(p)
else:
    print('全ての接続関係は正しいです')
