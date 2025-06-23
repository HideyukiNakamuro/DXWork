import openpyxl
import json
import pandas as pd

EXCEL_FILE = 'To-Be整理_after.xlsx'
SUMMARY_FILE = 'summary.json'

summary = []

wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    df = pd.DataFrame(ws.values)
    # サブグラフ名（B2）
    subgraph_name = str(df.iloc[1, 1]) if len(df) > 1 and len(df.columns) > 1 else f"Sheet_{sheet}"
    nodes = []
    for row in range(5, 100):
        if row >= len(df):
            break
        name_val = df.iloc[row, 1] if len(df.columns) > 1 else None  # B列
        node_val = df.iloc[row, 2] if len(df.columns) > 2 else None  # C列
        conn_info = df.iloc[row, 8] if len(df.columns) > 8 else None  # I列
        # 非表示判定
        hidden = 'x' if ws.row_dimensions.get(row+1) and ws.row_dimensions[row+1].hidden else 'o'
        nodes.append({
            'name': None if pd.isna(name_val) or str(name_val).strip() == '' else str(name_val),
            'node': None if pd.isna(node_val) or str(node_val).strip() == '' else str(node_val),
            'connect': None if pd.isna(conn_info) or str(conn_info).strip() == '' else str(conn_info),
            'display': hidden,
            'from': [
                {
                    'from_subgraph': '',
                    'from_node': ''
                }
            ],
            'memo': ''
        })
    summary.append({
        'sheet': subgraph_name,
        'subgraph': subgraph_name,
        'nodes': nodes
    })

with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"summary.jsonを出力しました。")
