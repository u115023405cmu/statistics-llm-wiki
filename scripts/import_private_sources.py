#!/usr/bin/env python3
"""從原始課程 ZIP 私下複製六份 PDF 到 raw；不得將 raw 提交公開 GitHub。"""
import argparse, csv, hashlib, pathlib, zipfile, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description='從原始 ZIP 私下匯入統計學講義')
    ap.add_argument('--archive',required=True,help='包含「統計學」資料夾的原始 ZIP 路徑')
    args=ap.parse_args()
    archive=pathlib.Path(args.archive)
    if not archive.is_file():
        sys.exit('找不到原始 ZIP：'+str(archive))
    with (ROOT/'wiki/sources/source_registry.csv').open(encoding='utf-8-sig',newline='') as fh:
        records=list(csv.DictReader(fh))
    with zipfile.ZipFile(archive) as z:
        members=z.namelist()
        for rec in records:
            fn=rec['filename']
            matches=[n for n in members if n.endswith('/統計學/'+fn)]
            if len(matches)!=1:
                sys.exit(f'來源不唯一或不存在：{fn}；找到 {len(matches)} 筆')
            raw=z.read(matches[0]); sha=hashlib.sha256(raw).hexdigest()
            if sha!=rec['sha256']:
                sys.exit(f'校驗失敗：{fn}；來源 ZIP 中的內容不同，拒絕覆寫')
            target=ROOT/'raw'/fn
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=sha:
                sys.exit(f'本機已有不同內容的檔案：{target}，請人工確認')
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            print('已私下匯入：',fn)
    print('提醒：請勿把 raw/ PDF 公開上傳至 GitHub。')

if __name__=='__main__':main()
