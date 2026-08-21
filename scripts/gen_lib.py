import re, html as H, os, json
import opencc

t2s = opencc.OpenCC('t2s')
s2t = opencc.OpenCC('s2t')
PROTECT = {'乾': 'QQQIANZZ'}
GAN_FIX = [('被髮而乾', 'BEIFAGAN')]
def smart(s):
    tmp = s
    for a, b in GAN_FIX: tmp = tmp.replace(a, b)
    for k, v in PROTECT.items(): tmp = tmp.replace(k, v)
    tmp = t2s.convert(tmp)
    for k, v in PROTECT.items(): tmp = tmp.replace(v, k)
    for a, b in GAN_FIX: tmp = tmp.replace(b, '被髮而干')
    return tmp

def emph(key_set, mark_set, bold_set, s, o):
    def build(ks, ms, bs, txt):
        if not txt: return ''
        phrases = sorted(set(ks) | set(ms) | set(bs), key=len, reverse=True)
        pat = re.compile('|'.join(re.escape(p) for p in phrases))
        def rep(m):
            g = m.group(0)
            if g in ks: return '<span class="key">' + g + '</span>'
            if g in ms: return '<mark>' + g + '</mark>'
            return '<b>' + g + '</b>'
        return pat.sub(rep, txt)
    return build(key_set, mark_set, bold_set, s), build([s2t.convert(p) for p in key_set], [s2t.convert(p) for p in mark_set], [s2t.convert(p) for p in bold_set], o)

def chapter_body(segs):
    s_parts, o_parts = [], []
    for seg in segs:
        if seg['t'] == 'q':
            s_parts.append('<blockquote>' + seg['s'] + '</blockquote>')
            o_parts.append('<blockquote>' + seg['o'] + '</blockquote>')
        elif seg['t'] == 'note':
            s_parts.append('<div class="note"><span class="badge">历代注解</span><div>' + seg['s'] + '</div></div>')
            o_parts.append('<div class="note"><span class="badge">历代注解</span><div>' + seg['o'] + '</div></div>')
        else:
            s_parts.append('<p>' + seg['s'] + '</p>')
            o_parts.append('<p>' + seg['o'] + '</p>')
    return '\n'.join(s_parts), '\n'.join(o_parts)

PAGE_LIMIT = 1100
def split_segs_into_pages(segs):
    pages = []
    cur = []
    cur_len = 0
    for seg in segs:
        l = len(seg['s'])
        if cur and cur_len + l > PAGE_LIMIT:
            pages.append(cur)
            cur = []
            cur_len = 0
        cur.append(seg)
        cur_len += l
    if cur: pages.append(cur)
    return pages

def page_html(book, ctitle, ch_title, ch_no, pg, total_pg, body_s, body_o, prev_link, next_link, ch_first, simp_dl, trad_dl):
    toolbar = '<div class="toolbar"><span class="t">☯ <a href="index.html">' + ctitle + '</a></span>'
    toolbar += '<span class="cnt">第 ' + str(ch_no) + ' 章 · ' + str(pg) + '/' + str(total_pg) + ' 页</span>'
    toolbar += '<button id="btnTg">切换到繁体原文</button><button id="btnNotes">隐藏注解</button><button id="btnTheme">🌙</button>'
    toolbar += '<span class="dl">⬇ <a href="../' + simp_dl + '" download>简体</a> · <a href="../' + trad_dl + '" download>原文</a></span></div>'
    nav = '<div class="nav">'
    nav += '<a href="' + (prev_link or '#') + '">← 上一页</a>' if prev_link else '<span></span>'
    nav += '<span class="mid"><a href="index.html">☰ 目录</a> · <a href="' + ch_first + '">' + ch_title + '</a></span>'
    nav += '<a href="' + (next_link or '#') + '">下一页 →</a>' if next_link else '<span></span>'
    nav += '</div>'
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        + '<meta name="viewport" content="width=device-width,initial-scale=1">'
        + '<title>' + ctitle + ' · ' + ch_title + '（' + str(pg) + '/' + str(total_pg) + '）</title>'
        + '<link rel="stylesheet" href="../assets/reader.css">'
        + '</head><body data-book="' + book + '" data-ch="' + str(ch_no) + '" data-pg="' + str(pg) + '">' + toolbar
        + '<div class="wrap"><h2 class="ch">' + ch_title + '<span class="pgno">第 ' + str(pg) + '/' + str(total_pg) + ' 页</span></h2>'
        + '<div class="content-simp">' + body_s + '</div>'
        + '<div class="content-trad">' + body_o + '</div>'
        + nav + '<p class="end">— ' + ctitle + ' · ' + ch_title + ' · ' + str(pg) + '/' + str(total_pg) + ' —</p></div>'
        + '<script src="../assets/reader.js"></script></body></html>')

def index_html(book, ctitle, subtitle, chapters, sections, full_reader, downloads, total_pages, notes_count):
    # chapters: list of (ch_no, (title, first, pcount))
    # sections: list of (name, start, end) 1-based inclusive, or None
    def item_html(ch_no, title, first, pcount):
        return '<li data-ch="' + str(ch_no) + '"><a href="' + first + '"><span class="no">%02d</span>' % ch_no             + H.escape(title) + '<span class="pg">' + str(pcount) + '页</span></a></li>'
    body_blocks = []
    if sections:
        for sname, start, end in sections:
            sub = [c for c in chapters if start <= c[0] <= end]
            if not sub: continue
            pages = sum(x[1][2] for x in sub)
            items = ''.join(item_html(n, t, f, p) for n, (t, f, p) in sub)
            body_blocks.append('<div class="section"><h3 class="sec-title">' + H.escape(sname)
                + '<span>' + str(len(sub)) + ' 章 · ' + str(pages) + ' 页</span></h3>'
                + '<ul class="toclist">' + items + '</ul></div>')
    else:
        items = ''.join(item_html(n, t, f, p) for n, (t, f, p) in chapters)
        body_blocks.append('<div class="section"><ul class="toclist">' + items + '</ul></div>')
    meta = '<div class="bookmeta">'
    if full_reader: meta += '<a class="btn" href="../' + full_reader + '">📖 整卷连读</a>'
    for dl in downloads: meta += '<a class="btn" href="../' + dl + '" download>⬇ 下载</a>'
    meta += '</div>'
    stats = ('<div class="stats"><span><b>' + str(len(chapters)) + '</b>章</span>'
        + '<span><b>' + str(total_pages) + '</b>页</span>'
        + '<span><b>' + str(notes_count) + '</b>段注解</span></div>')
    cont = '<div id="continueBox" style="display:none"><a class="btn continue" id="continueLink" href="#">📖 继续阅读：<span id="continueLabel"></span></a></div>'
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        + '<meta name="viewport" content="width=device-width,initial-scale=1">'
        + '<title>' + ctitle + ' · 章节目录</title>'
        + '<link rel="stylesheet" href="../assets/reader.css">'
        + '</head><body data-book="' + book + '">'
        + '<div class="toolbar"><span class="t">☯ <a href="../index.html">道教九经</a></span>'
        + '<span><a href="../index.html">← 藏经阁</a></span><button id="btnTheme">🌙</button></div>'
        + '<div class="wrap tocpage"><div class="bookhead"><div class="seal">☯</div>'
        + '<h1>' + ctitle + '</h1>'
        + '<p class="sub">' + subtitle + '</p>' + stats
        + '<div class="actions">' + cont + meta + '</div></div>'
        + ''.join(body_blocks)
        + '<p class="end">— ' + ctitle + ' —</p></div>'
        + '<script src="../assets/reader.js"></script></body></html>')

def split_chapters(lines, note_startswith):
    chapters = []
    cur_title = None
    cur = []
    seen_title = False
    for ln in lines:
        l = ln.strip()
        if not l: continue
        if l.startswith('# ') and not seen_title:
            seen_title = True
            continue
        is_h = False; t = ''
        if l.startswith('## '):
            t = l[3:].strip(); is_h = True
        elif re.match(r'^【[^】]+】$', l):
            t = l[1:-1].strip(); is_h = True
        elif l.startswith('# ') and seen_title:
            t = l[2:].strip(); is_h = True
        if is_h:
            if cur_title is not None or cur:
                chapters.append([cur_title or '开篇', cur])
            cur_title = t
            cur = []
        elif l.startswith('> '):
            cur.append('{Q}' + l[2:].strip())
        elif any(l.startswith(p) for p in note_startswith):
            cur.append('{N}' + l)
        elif l.startswith('「') and l.endswith('」') and len(l) > 40:
            cur.append('{N}' + l)
        else:
            cur.append(l)
    if cur_title is not None or cur:
        chapters.append([cur_title or '开篇', cur])
    return chapters

def build_book(slug, ctitle, subtitle, srcfile, key, mark, bold, note_startswith, full_reader=None, downloads=(), sections=None):
    lines = open(srcfile, encoding='utf-8').read().split('\n')
    chapters = split_chapters(lines, note_startswith)
    os.makedirs(slug, exist_ok=True)
    ch_data = []
    total_notes = 0
    for title, cls in chapters:
        segs = []
        for l in cls:
            is_note = l.startswith('{N}')
            is_quote = l.startswith('{Q}')
            text = l[3:] if (is_note or is_quote) else l
            simp, orig = smart(text), text
            if is_quote: t = 'q'
            elif is_note: t = 'note'
            else: t = 'p'
            s = H.escape(simp); o = H.escape(orig)
            if t in ('p', 'note'):
                s, o = emph(key, mark, bold, s, o)
            if t == 'note': total_notes += 1
            segs.append({'t': t, 's': s, 'o': o})
        ch_data.append((title, split_segs_into_pages(segs)))
    total_ch = len(ch_data)
    simp_dl = downloads[0] if downloads else (slug + '_simp.txt')
    trad_dl = downloads[1] if len(downloads) > 1 else (slug + '.txt')
    total_pages = 0
    for ci, (title, pages) in enumerate(ch_data, 1):
        total_pages += len(pages)
        for pi, page_segs in enumerate(pages, 1):
            body_s, body_o = chapter_body(page_segs)
            prev = None
            if pi > 1: prev = 'c%02d_%02d.html' % (ci, pi - 1)
            elif ci > 1: prev = 'c%02d_%02d.html' % (ci - 1, len(ch_data[ci - 2][1]))
            nxt = None
            if pi < len(pages): nxt = 'c%02d_%02d.html' % (ci, pi + 1)
            elif ci < total_ch: nxt = 'c%02d_01.html' % (ci + 1)
            ch_first = 'c%02d_01.html' % ci
            open(slug + '/c%02d_%02d.html' % (ci, pi), 'w', encoding='utf-8').write(
                page_html(slug, ctitle, title, ci, pi, len(pages), body_s, body_o, prev, nxt, ch_first, simp_dl, trad_dl))
    chapters_info = [(ci, (t, 'c%02d_01.html' % ci, len(pages))) for ci, (t, pages) in enumerate(ch_data, 1)]
    open(slug + '/index.html', 'w', encoding='utf-8').write(
        index_html(slug, ctitle, subtitle, chapters_info, sections, full_reader, downloads, total_pages, total_notes))
    return total_ch, [t for t, _ in ch_data]
