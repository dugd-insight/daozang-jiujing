# ☯ 道藏九经 · 精校阅读系统

道教九部经典（《周易参同契》《悟真篇》《太乙金华宗旨》《性命圭旨》《黄庭经》《南华真经》《阴符经》《坐忘论》《清静经》）的精校在线阅读站点。

功能特性：
- 分页阅读：按章 x 页细分，单页 8-15KB，上一页/下一页/目录导航
- 续读记忆：自动记录「书 → 章 → 页 + 滚动位置」，目录页一键「继续阅读」，已读章节打勾
- 简繁对照：一键切换简体正文 / 繁体原文（OpenCC 转换，八卦专名如「乾」按规范保留）
- 历代注解：郭象注/成玄英疏、李筌疏、俞琰发挥、翁葆光注、闵一得按、历代仙真口诀等，灰底块显示，可一键隐藏
- 三级高亮：金底总诀 / 橙底关键句 / 加粗术语，词库可查
- 全文搜索：九经章节级全文检索（search.html）
- 深色模式 / 打印友好：主题切换按钮，@media print 打印样式
- 零依赖：运行仅需 Node 16+（或任意静态服务器）

## 目录结构

    server.js                 # 静态服务器（Node 原生，MIME/gzip/缓存/安全头/304）
    package.json              # npm start = node server.js
    Dockerfile                # 多阶段构建（python 生成 → node 运行）
    docker-compose.yml
    deploy/
      nginx.conf.example      # Nginx 托管/反代示例
      daozang.service         # systemd 自启示例
    scripts/                  # 生成管线
      gen_lib.py              # 分页/目录/搜索索引生成核心
      gen_configs.py          # 九经配置（书名/高亮词/注家/分节）
      generate_all.py         # 一键重建站点
      build_search_index.py   # 生成搜索索引
    site/                     # 站点产物（部署时就是它）
      index.html              # 藏经阁首页
      search.html             # 全文搜索
      assets/                 # 共享 CSS/JS
      nanhua/ xingming/ ...   # 各书分页目录
      reader_*.html           # 各书整卷连读版
      *.txt                   # 原文/简体全文（下载）
      reports/                # deepread 精读报告

## 本地运行

方式一（Node，推荐，零依赖）：

    npm start        # 或 node server.js
    # 访问 http://127.0.0.1:8123/

方式二（任意静态服务器）：

    cd site && python3 -m http.server 8123

端口/目录可配：node server.js --port 9000 --dir ./site --host 0.0.0.0（也支持环境变量 PORT/HOST）。

## 一键重建站点

生成管线需要 Python 3 + OpenCC：

    pip install opencc-python-reimplemented
    python3 scripts/generate_all.py

重建会重新生成全部书的分页页面、目录页与搜索索引（数据源在 site/*.txt）。

## Docker 部署

    docker compose up -d --build     # 构建镜像并后台运行（8123 端口）

多阶段构建：阶段一用 python+OpenCC 生成站点，阶段二仅打包 node 运行镜像（小体积）。

## 服务器部署

- Nginx：参考 deploy/nginx.conf.example（gzip/缓存/安全头）
- systemd：deploy/daozang.service（开机自启）
- 推荐目录 /opt/daozang，将本仓库内容放置于此

## 新增一部经典

1. 将繁体原文放入 site/（形如 xxx.txt；章节用「## 章名」或「【章名】」标记；注解行以「XXX曰：」开头即识别为历代注解块）
2. 在 scripts/gen_configs.py 增加一条 build_book(...) 配置（书名/高亮词/注家/分节）
3. 运行 python3 scripts/generate_all.py 重建
4. 在 site/index.html 增加一张卡片

## 说明

- 文本源：中国哲学书电子化计划（ctext.org）、《庄子集释》等公版古籍整理
- 繁体底本未改一字；简体为 OpenCC 机械转换，八卦专名（乾/坤/坎/离等）依规范保留
- 历代注解均引自真实注本原文（郭象、成玄英、李筌、俞琰、翁葆光、闵一得等）
- 仅作个人研读整理，请勿用于商业用途
