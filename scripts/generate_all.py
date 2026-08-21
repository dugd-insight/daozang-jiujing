#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键重建站点: python3 scripts/generate_all.py
从 site/ 下的原文数据重新生成全部分页页面与目录页。"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..', 'site'))

def main():
    os.chdir(SITE)
    sys.path.insert(0, HERE)
    print('☯ 重建站点: ' + SITE)
    # 1) 生成分页页面
    with open(os.path.join(HERE, 'gen_configs.py'), encoding='utf-8') as f:
        exec(compile(f.read(), 'gen_configs.py', 'exec'))
    # 2) 生成搜索索引
    from build_search_index import build_index
    build_index(SITE)
    print('✅ 全部完成')

if __name__ == '__main__':
    main()
