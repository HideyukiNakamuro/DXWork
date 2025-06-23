import json
import re

SUMMARY_FILE = 'summary.json'
OUTPUT_FILE = 'output.mmd'
LOG_FILE = 'output.log'

# - とひらがな・カタカナも許容
MERMAID_SAFE_PATTERN = re.compile(r'[^a-zA-Z0-9_\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF\-]')

def sanitize_name(name, kind, context):
    if not name or str(name).strip() == '':
        return None
    original = str(name)
    # スペースは削除、他は正規表現で置換
    sanitized = original.replace(' ', '').replace('\t', '')
    if sanitized != original:
        log(f"警告: {kind}名 '{original}' からスペース・タブを削除しました（{context}）")
    sanitized = MERMAID_SAFE_PATTERN.sub('_', sanitized)
    if sanitized != original and sanitized == original.replace(' ', '').replace('\t', ''):
        # スペース・タブ以外の変換があった場合のみ警告
        log(f"警告: {kind}名 '{original}' を '{sanitized}' に変換しました（{context}）")
    if not sanitized or sanitized.strip('_') == '':
        log(f"警告: {kind}名 '{original}' は無効なため排除しました（{context}）")
        return None
    return sanitized

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str(msg) + '\n')

def main():
    with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write('flowchart LR\n')  # 横並び指定
        node_ids = {}
        name_to_node = {}  # (subgraph, name) -> node のマッピング
        for group in summary:
            subgraph_name = sanitize_name(group['subgraph'], 'サブグラフ', f"sheet:{group['sheet']}")
            if not subgraph_name:
                continue
            nodes = set()
            node_lines = []
            for node in group['nodes']:
                node_name = sanitize_name(node.get('node'), 'ノード', f'subgraph:{subgraph_name}')
                name_name = sanitize_name(node.get('name'), 'ノード名', f'subgraph:{subgraph_name}')
                if not node_name or node.get('display') == 'x':
                    continue
                if node_name in nodes:
                    log(f"警告: サブグラフ '{subgraph_name}' 内でノード '{node_name}' が重複したため排除")
                    continue
                nodes.add(node_name)
                node_id = f'{subgraph_name}_{node_name}'
                node_ids[(subgraph_name, node_name)] = node_id
                if name_name:
                    name_to_node[(subgraph_name, name_name)] = node_name
                node_lines.append(f'    {node_id}[{node_name}]')
            if node_lines:
                out.write(f'  subgraph {subgraph_name}\n')
                for line in node_lines:
                    out.write(line + '\n')
                out.write('  end\n')
        # 接続線描画（複数入力対応）
        for group in summary:
            subgraph_name = sanitize_name(group['subgraph'], 'サブグラフ', f"sheet:{group['sheet']}")
            for node in group['nodes']:
                node_name = sanitize_name(node.get('node'), 'ノード', f'subgraph:{subgraph_name}')
                if not node_name or node.get('display') == 'x':
                    continue
                froms = node.get('from', [])
                if isinstance(froms, dict):
                    froms = [froms]
                for from_info in froms:
                    from_sub = from_info.get('from_subgraph', '')
                    from_node = from_info.get('from_node', '')
                    if from_sub and from_node:
                        from_sub_s = sanitize_name(from_sub, 'サブグラフ', '接続元')
                        from_node_s = sanitize_name(from_node, 'ノード', '接続元')
                        # node属性でID検索、なければname→node変換して再検索
                        from_id = node_ids.get((from_sub_s, from_node_s))
                        if not from_id:
                            alt_node = name_to_node.get((from_sub_s, from_node_s))
                            if alt_node:
                                from_id = node_ids.get((from_sub_s, alt_node))
                        to_id = node_ids.get((subgraph_name, node_name))
                        if from_id and to_id:
                            out.write(f'  {from_id} --> {to_id}\n')
                        else:
                            log(f"警告: 接続線エラー from=({from_sub_s},{from_node_s}, id={from_id}) to=({subgraph_name},{node_name}, id={to_id})")

if __name__ == '__main__':
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('')
    main()
    print(f"Mermaidグラフを{OUTPUT_FILE}に出力しました。ログ: {LOG_FILE}")
