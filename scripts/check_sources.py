#!/usr/bin/env python3
"""用標準函式庫檢查 raw/ 的六份 PDF 是否存在且 SHA-256 與來源登記相符。"""
import csv,hashlib,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
with (ROOT/'wiki/sources/source_registry.csv').open(encoding='utf-8-sig',newline='') as fh:
    records=list(csv.DictReader(fh))
failures=0
for row in records:
    p=ROOT/row['local_location']
    if not p.is_file():
        print('缺少：',row['filename']);failures+=1;continue
    if p.suffix.lower()!='.pdf' or not p.read_bytes()[:5]==b'%PDF-':
        print('格式錯誤：',row['filename']);failures+=1;continue
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    if digest!=row['sha256']:
        print('內容不符：',row['filename']);failures+=1;continue
    print('通過：',row['filename'])
print(f'檢查完畢：{len(records)-failures}/{len(records)} 份通過')
sys.exit(0 if failures==0 else 1)
