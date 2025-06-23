import pandas as pd
import os

file1 = 'To-Be整理_before.xlsx'
file2 = 'To-Be整理_after.xlsx'
report_file = 'report.md'

def append_report(lines):
    with open(report_file, 'a', encoding='utf-8') as f:
        if isinstance(lines, list):
            f.write('\n'.join(lines) + '\n')
        else:
            f.write(str(lines) + '\n')

# レポート初期化
def init_report():
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('# Excel差分レポート\n')

# ファイル存在チェック
def check_file(path):
    if not os.path.exists(path):
        append_report(f"ファイルが見つかりません: {path}")
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

init_report()
append_report('ファイル存在チェック中...')
check_file(file1)
check_file(file2)
append_report('ファイル存在チェック完了')

# Excelファイルのシート一覧取得
def get_sheets(file):
    xls = pd.ExcelFile(file)
    return set(xls.sheet_names)

append_report('シート一覧取得中...')
sheets1 = get_sheets(file1)
sheets2 = get_sheets(file2)
append_report('シート一覧取得完了')

added_sheets = sheets2 - sheets1
removed_sheets = sheets1 - sheets2
common_sheets = sheets1 & sheets2

if added_sheets:
    append_report([f"## 追加されたシート\n- {', '.join(added_sheets)}\n"])
if removed_sheets:
    append_report([f"## 削除されたシート\n- {', '.join(removed_sheets)}\n"])

for sheet in common_sheets:
    append_report(f"シート '{sheet}' の比較中...")
    df1 = pd.read_excel(file1, sheet_name=sheet)
    df2 = pd.read_excel(file2, sheet_name=sheet)
    if df1.equals(df2):
        append_report(f"## シート '{sheet}'\n差分なし\n")
    else:
        append_report(f"## シート '{sheet}' 差分あり\n")
        try:
            diff1 = pd.concat([df1, df2]).drop_duplicates(keep=False)
            if not diff1.empty:
                append_report(f"### 差分内容\n{diff1.to_markdown(index=False)}\n")
            else:
                append_report("差分の詳細取得に失敗または差分が特定できませんでした。\n")
        except Exception as e:
            append_report(f"差分の詳細取得でエラー: {e}\n")
    append_report(f"シート '{sheet}' の比較完了\n")

append_report('全処理完了')
print(f"レポートを {report_file} に出力しました。")
