#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成全站搜索索引 site/search-index.json
索引: 书 → 章（章号/标题/页数/首页链接/简体全文），用于客户端全文搜索。"""
import os, re, json

BOOKS = [
    ('nanhua', '南华真经（庄子）', 'nanhua_zhenjing_simp.txt'),
    ('xingming', '性命圭旨（性命双修万神圭旨）', 'xingming_guizhi_simp.txt'),
    ('cantongqi', '周易参同契', 'cantongqi_simp.txt'),
    ('wuzhenpian', '悟真篇', 'wuzhenpian_simp.txt'),
    ('huangting', '黄庭经（内景·外景）', 'huangting_jing_simp.txt'),
    ('jinhua', '太乙金华宗旨', 'taiji_jinhua_zongzhi_simp.txt'),
    ('zuowang', '坐忘论', 'zuowanglun_simp.txt'),
    ('yinfu', '黄帝阴符经', 'yinfujing_simp.txt'),
    ('qingjing', '太上老君说常清静经', 'qingjingjing_simp.txt'),
]

def strip_markup(t):
    return re.sub(r'<[^>]+>', '', t)

def build_index(site_dir):
    index = {'version': 1, 'books': []}
    for slug, title, simp_file in BOOKS:
        fp = os.path.join(site_dir, simp_file)
        if not os.path.exists(fp):
            print('  跳过(无文件):', simp_file)
            continue
        lines = open(fp, encoding='utf-8').read().split('\n')
        chapters = []
        cur = None
        no = 1  # 1 = 开篇
        for l in lines:
            t = l.strip()
            if t.startswith('## '):
                if cur is not None:
                    chapters.append(cur)
                no += 1
                cur = {'no': no, 'title': t[3:].strip(), 'text': []}
            elif cur is not None and t:
                cur['text'].append(strip_markup(t))
        if cur is not None:
            chapters.append(cur)
        # 页数: 从目录页解析 (或估算)
        idx_fp = os.path.join(site_dir, slug, 'index.html')
        page_counts = {}
        if os.path.exists(idx_fp):
            h = open(idx_fp, encoding='utf-8').read()
            for m in re.finditer(r'data-ch="(\d+)"[^>]*>.*?<span class="pg">(\d+)页', h):
                page_counts[int(m.group(1))] = int(m.group(2))
        books_ch = []
        for ch in chapters:
            no = ch['no']
            pcount = page_counts.get(no, 1)
            books_ch.append({
                'no': no,
                'title': ch['title'],
                'pages': pcount,
                'first': 'c%02d_01.html' % no,
                'text': ''.join(ch['text'])
            })
        index['books'].append({'slug': slug, 'title': title, 'chapters': books_ch})
        print('  索引:', title, '→', len(books_ch), '章')
    out = os.path.join(site_dir, 'search-index.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))
    print('✅ 搜索索引已写入:', out, '(%d 字节)' % os.path.getsize(out))
    return index

if __name__ == '__main__':
    build_index(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')))
