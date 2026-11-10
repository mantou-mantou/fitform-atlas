#!/usr/bin/env python3
"""Validate FitForm Atlas JSON contract and local illustration assets (standard library only)."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'exercises.json'
SLUG = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
EXERCISE_KEYS = {'id','name','nameEn','category','level','summary','intro','equipment','muscles','steps','mistakes','safetyTips','keywords','illustration','sources'}
CATEGORY_KEYS = {'id','label','description'}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def check_list_text(value, at, errs, minimum=0):
    if not isinstance(value, list) or len(value) < minimum:
        errs.append(f'{at}: 至少要有 {minimum} 個項目（陣列）')
        return
    for idx, item in enumerate(value):
        if not nonempty(item): errs.append(f'{at}[{idx}]: 需要非空字串')


def validate(doc, root=ROOT):
    errs = []
    if not isinstance(doc, dict): return ['根節點必須是 object']
    expected_root = {'schemaVersion','lastUpdated','categories','exercises'}
    if set(doc) != expected_root: errs.append(f'根節點欄位錯誤：缺少 {sorted(expected_root-set(doc))}；多出 {sorted(set(doc)-expected_root)}')
    if doc.get('schemaVersion') != '1.0.0': errs.append('schemaVersion 目前必須是 1.0.0')
    try: dt.date.fromisoformat(doc.get('lastUpdated', ''))
    except (TypeError, ValueError): errs.append('lastUpdated 必須使用 YYYY-MM-DD')
    cats = doc.get('categories')
    if not isinstance(cats, list) or not cats: errs.append('categories 必須是非空陣列'); cats = []
    cat_ids = set()
    for i, cat in enumerate(cats):
        at = f'categories[{i}]'
        if not isinstance(cat, dict): errs.append(f'{at} 必須是物件'); continue
        if set(cat) != CATEGORY_KEYS: errs.append(f'{at} 欄位不符：{sorted(set(cat)^CATEGORY_KEYS)}')
        key = cat.get('id')
        if not isinstance(key, str) or not SLUG.fullmatch(key): errs.append(f'{at}.id 不符合 kebab-case')
        if key in cat_ids: errs.append(f'{at}.id 重複：{key}')
        cat_ids.add(key)
        for field in ['label','description']:
            if not nonempty(cat.get(field)): errs.append(f'{at}.{field} 不可空白')
    items = doc.get('exercises')
    if not isinstance(items, list) or not items: errs.append('exercises 必須是非空陣列'); return errs
    ids = set()
    for i, ex in enumerate(items):
        at = f'exercises[{i}]'
        if not isinstance(ex, dict): errs.append(f'{at} 必須是物件'); continue
        if set(ex) != EXERCISE_KEYS: errs.append(f'{at} 欄位不符：缺少 {sorted(EXERCISE_KEYS-set(ex))}；多出 {sorted(set(ex)-EXERCISE_KEYS)}')
        slug = ex.get('id')
        if not isinstance(slug, str) or not SLUG.fullmatch(slug): errs.append(f'{at}.id 不符合 kebab-case')
        if slug in ids: errs.append(f'{at}.id 重複：{slug}')
        ids.add(slug)
        for field in ('name','nameEn','summary','intro'):
            if not nonempty(ex.get(field)): errs.append(f'{at}.{field} 必須是非空字串')
        if ex.get('category') not in cat_ids: errs.append(f'{at}.category 不在 categories 中')
        if ex.get('level') not in ('beginner','intermediate','advanced'): errs.append(f'{at}.level 不合法')
        check_list_text(ex.get('equipment'), f'{at}.equipment', errs, 1)
        check_list_text(ex.get('safetyTips'), f'{at}.safetyTips', errs, 2)
        check_list_text(ex.get('keywords'), f'{at}.keywords', errs)
        muscles = ex.get('muscles')
        if not isinstance(muscles,dict) or set(muscles) != {'primary','secondary'}:
            errs.append(f'{at}.muscles 必須有 primary 與 secondary')
        else:
            check_list_text(muscles['primary'], f'{at}.muscles.primary', errs, 1)
            check_list_text(muscles['secondary'], f'{at}.muscles.secondary', errs)
        for field,minimum in [('steps',3),('mistakes',2)]:
            arr=ex.get(field)
            if not isinstance(arr,list) or len(arr)<minimum: errs.append(f'{at}.{field} 至少 {minimum} 筆'); continue
            for j,item in enumerate(arr):
                if not isinstance(item,dict) or set(item) != {'title','description'} or not all(nonempty(item.get(k)) for k in ('title','description')):
                    errs.append(f'{at}.{field}[{j}] 必須含非空 title 和 description')
        ill = ex.get('illustration')
        expected = f'assets/illustrations/{slug}.svg'
        if ill != expected: errs.append(f'{at}.illustration 必須為 {expected}')
        elif not (root / ill).is_file(): errs.append(f'{at}.illustration 找不到檔案：{ill}')
        sources=ex.get('sources')
        if not isinstance(sources,list) or not sources: errs.append(f'{at}.sources 至少一筆')
        else:
            for j,item in enumerate(sources):
                if not isinstance(item,dict) or set(item) != {'title','url'} or not nonempty(item.get('title')) or not nonempty(item.get('url')):
                    errs.append(f'{at}.sources[{j}] 必須含 title 和 url'); continue
                url=urlparse(item['url'])
                if url.scheme != 'https' or not url.netloc: errs.append(f'{at}.sources[{j}].url 必須是 HTTPS 網址')
    return errs


def main():
    parser=argparse.ArgumentParser(description='Validate FitForm Atlas content contract')
    parser.add_argument('--data', type=Path, default=DATA, help='path to exercises.json')
    parser.add_argument('--root', type=Path, default=ROOT, help='project root for SVG assets')
    args=parser.parse_args()
    try: doc=json.loads(args.data.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc:
        print(f'FAIL：無法讀取合法 JSON：{exc}'); return 1
    errs=validate(doc,args.root)
    if errs:
        print(f'FAIL：找到 {len(errs)} 個問題')
        for msg in errs: print('  - '+msg)
        return 1
    print(f'PASS：{len(doc["exercises"])} 筆動作、{len(doc["categories"])} 個分類，schema、來源及插畫均有效')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
