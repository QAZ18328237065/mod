# -*- coding: utf-8 -*-
"""《聚焦地中海》一键构建脚本
============================================================
用法：python build_focus_east_asia.py
流程：landed_titles 组装 → capital 校验 → 保留省份/default.map
      → 框架空壳 → titles 历史裁剪 → 书签/组/挑战角色
      → 自建帝国本地化与历史 → 汇总

以后调整地图/法理只需改下方【配置区】：
  · 整文件复制            → COPY_FILES
  · 提取原版帝国(可裁剪王国) → EXTRACT_EMPIRES
  · 块转移(改法理)         → MOVE_BLOCKS
  · 块删除                → REMOVE_FROM
  · 自建帝国               → NEW_EMPIRES
  · 书签剧本/删除角色/组    → BOOKMARKS_KEEP / BOOKMARK_DROP_CHARS / GROUPS_KEEP
============================================================
"""
import re, os, glob, shutil

# ==================== 配置区 ====================
GAME = r"D:\Steam\steamapps\common\Crusader Kings III\game"
EA   = os.path.dirname(os.path.abspath(__file__))
GAME_LT = os.path.join(GAME, "common", "landed_titles")
EA_LT   = os.path.join(EA, "common", "landed_titles")

# 1) 整文件复制（原版同内容覆盖；文件内头衔全部保留区）
COPY_FILES = []   # 无整文件复制（全部从 00_landed_titles 提取）

# 2) 从原版提取帝国 → 主文件
MAIN_FILE = "00_middle_east.txt"
EXTRACT_EMPIRES = {
    "e_arabia": None,
    "e_byzantium": None,
    "e_persia": None,
    "e_carpathia": None,
    "e_italy": None,
    "e_maghreb": ["k_maghreb", "k_canarias", "k_tahert", "k_africa"],  # 删除 k_anbiya / k_sahara
    "e_latin_empire": None,           # 拉丁帝国
    "e_spain": None,                  # 伊比利亚全 10 王国
    "e_france": None,                 # 法兰西全 4 王国（恢复 k_france / k_brittany）
    "e_germany": None,                # 德意志全 5 王国
}

# 2b) 按帝国删除王国（提取后执行）——已全部恢复原版法理，无删除
DROP_KINGDOMS = {}

# 3) 块转移（改法理）——已全部恢复原版法理，k_sicily/k_venice 归拜占庭
MOVE_BLOCKS = []

# 4) 块删除——已全部恢复原版法理，d_oman 归阿拉伯
REMOVE_FROM = {}

# 4b) 删除后需清空的历史文件
TITLES_DROP = []

# 5) 自建帝国
NEW_EMPIRES = []

# 6) 书签与默认剧本
BOOKMARKS_KEEP = ["bm_867_persia", "bm_867_iberia", "bm_867_carolingians",
                  "bm_1066_iberia",
                  "bm_1178_call_of_the_empire", "bm_1178_swords_of_faith"]
BOOKMARK_DROP_CHARS = ["Ism"]   # 图兰角色伊司马仪·萨曼尼（领地 c_bukhara 区域外）
GROUPS_KEEP = ["bm_group_867", "bm_group_1066", "bm_group_1178"]
DEFAULT_BOOKMARK = "bm_867_persia"

# ==================== 通用函数 ====================
def read(p):
    return open(p, "r", encoding="utf-8-sig", errors="ignore").read()

def write(p, s):
    with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(s)

def find_block(text, start):
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start+1:i], i
        i += 1
    raise ValueError("unbalanced")

def get_block(text, name):
    m = re.search(r'(?m)^\s*%s\s*=\s*\{' % re.escape(name), text)
    if not m:
        return None
    body, end = find_block(text, m.end()-1)
    return text[m.start():end+1]

def append_to(text, parent, full):
    m = re.search(r'(?m)^\s*%s\s*=\s*\{' % parent, text)
    if not m:
        raise SystemExit(f"!! 找不到父块 {parent}")
    body, end = find_block(text, m.end()-1)
    return text[:m.start()] + text[m.start():end].rstrip() + "\n" + full.rstrip() + "\n}\n" + text[end+1:]

def remove_from(text, parent, child):
    m = re.search(r'(?m)^\s*%s\s*=\s*\{' % parent, text)
    if not m:
        raise SystemExit(f"!! 找不到父块 {parent}")
    body, end = find_block(text, m.end()-1)
    cm = re.search(r'(?m)^\s*%s\s*=\s*\{' % child, body)
    if not cm:
        return text, False
    cbody, cend = find_block(body, cm.end()-1)
    new_body = body[:cm.start()] + body[cend+1:]
    return text[:m.end()] + new_body + "\n}\n" + text[end+1:], True

def resolve(spec):
    if spec.startswith("GAME:"):
        return os.path.join(GAME_LT, spec[5:])
    return os.path.join(EA_LT, spec[4:])

def mkdirs(path):
    os.makedirs(path, exist_ok=True)

# ==================== 构建流程 ====================
def step_copy():
    print("[1/9] 复制原版文件")
    for f in COPY_FILES:
        shutil.copy(os.path.join(GAME_LT, f), os.path.join(EA_LT, f))
        print(f"    已复制 {f}")

def step_new_empires():
    print("[2/9] 自建帝国骨架")
    for emp in NEW_EMPIRES:
        p = os.path.join(EA_LT, emp["file"])
        body = "@always_primary_score = 1000\n" \
               "@better_than_the_alternatives_score = 50\n" \
               "@correct_culture_primary_score = 100\n" \
               "@never_primary_score = -1000\n"
        body += f"# 自建帝国 {emp['zh']}\n{emp['name']} = {{\n"
        body += f"\tcolor = {{ {emp['color'][0]} {emp['color'][1]} {emp['color'][2]} }}\n"
        body += f"\tcapital = {emp['capital']}\n}}\n"
        write(p, body)
        print(f"    已创建 {emp['file']}")

def step_extract():
    print(f"[3/9] 提取原版帝国 → {MAIN_FILE}")
    lt_main = read(os.path.join(GAME_LT, "00_landed_titles.txt"))
    hdr = ""
    for line in lt_main.split("\n"):
        if line.startswith("@"):
            hdr += line + "\n"
        else:
            break
    parts = [hdr]
    for emp, keep_kingdoms in EXTRACT_EMPIRES.items():
        block = get_block(lt_main, emp)
        if not block:
            raise SystemExit(f"!! 找不到 {emp}")
        body = block[block.find('{')+1:block.rfind('}')]   # 内部体（不含外层包裹）
        if keep_kingdoms is not None:
            for m in re.finditer(r'(?m)^\s*k_[a-z0-9_\-\x27]+\s*=\s*\{', body):
                kname = m.group(0).split()[0]
                if kname not in keep_kingdoms:
                    km = re.search(r'(?m)^\s*%s\s*=\s*\{' % kname, body)
                    _, end = find_block(body, km.end()-1)
                    body = body[:km.start()] + body[end+1:]
                    print(f"    {emp} 删除 {kname}")
        for kname in DROP_KINGDOMS.get(emp, []):
            km = re.search(r'(?m)^\s*%s\s*=\s*\{' % kname, body)
            if not km:
                raise SystemExit(f"!! {emp} 找不到要删除的 {kname}")
            _, end = find_block(body, km.end()-1)
            body = body[:km.start()] + body[end+1:]
            print(f"    {emp} 删除 {kname}")
        parts.append(f"{emp} = {{\n{body.rstrip()}\n}}\n")
    write(os.path.join(EA_LT, MAIN_FILE), "".join(parts))
    print(f"    {MAIN_FILE} 完成")

def step_move_remove():
    print("[4/9] 块转移与删除")
    # 转移
    for src_spec, src_parent, block, dst_spec, dst_parent in MOVE_BLOCKS:
        st = read(resolve(src_spec))
        if src_parent:
            sp = get_block(st, src_parent)
            if not sp:
                raise SystemExit(f"!! {src_spec} 找不到 {src_parent}")
        else:
            sp = st
        full = get_block(sp, block)
        if not full:
            raise SystemExit(f"!! {src_spec} 找不到 {block}")
        # 源在 mod 文件 → 移出
        if src_spec.startswith("MOD:"):
            p = resolve(src_spec)
            t = read(p)
            t, ok = remove_from(t, src_parent, block)
            if not ok:
                raise SystemExit(f"!! {src_spec} 的 {src_parent} 无 {block}")
            write(p, t)
        # 目标追加
        dp = resolve(dst_spec)
        t = read(dp)
        t = append_to(t, dst_parent, full)
        write(dp, t)
        print(f"    {block} → {dst_spec} 的 {dst_parent}")
    # 删除（父块可能由转移产生，故在转移后执行）
    for (fspec, parent), children in REMOVE_FROM.items():
        p = resolve(fspec)
        t = read(p)
        for child in children:
            t, ok = remove_from(t, parent, child)
            if not ok:
                raise SystemExit(f"!! {fspec} 的 {parent} 无 {child}")
            print(f"    删除 {child} (from {parent})")
        write(p, t)

def step_capital():
    print("[5/9] capital 校验")
    defined = set()
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        defined |= set(re.findall(r'(?m)^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', read(f)))
    cap_re = re.compile(r'^\s*capital\s*=\s*(c_[a-zA-Z0-9_\-]+)[^\n]*\n', re.M)
    rm = 0
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        t = read(f)
        new = cap_re.sub(lambda m: "" if m.group(1) not in defined else m.group(0), t)
        if new != t:
            rm += len(cap_re.findall(t)) - len(cap_re.findall(new))
            write(f, new)
            print(f"    capital 修复: {os.path.basename(f)}")
    print(f"    删除 capital 行: {rm}")

def step_map():
    print("[6/9] 保留省份 + default.map")
    NAME_RE = r'[a-zA-Z0-9_\-\x27]+'
    kept_prov = set()
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        if os.path.basename(f) == "10_world_framework.txt":
            continue
        t = read(f)
        for bm in re.finditer(r'^\s*(b_%s)\s*=\s*\{' % NAME_RE, t, re.M):
            bbody, _ = find_block(t, bm.end()-1)
            pv = re.search(r'^\s*province\s*=\s*(\d+)', bbody, re.M)
            if pv:
                kept_prov.add(int(pv.group(1)))
    print(f"    保留省份: {len(kept_prov)}")
    # 全省份全集（definition.csv，排除 ID 0 哨兵）与海/湖
    dc = read(os.path.join(GAME, "map_data", "definition.csv"))
    all_ids = set(int(m.group(1)) for m in re.finditer(r'(?m)^(\d+)[;,]', dc))
    all_ids.discard(0)
    vmap = read(os.path.join(GAME, "map_data", "default.map"))
    sea_lake = set()
    for m in re.finditer(r'(?:sea_zones|lakes)\s*=\s*(RANGE|LIST)\s*\{ ([^}]+) \}', vmap):
        nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
        if m.group(1) == 'RANGE' and len(nums) == 2:
            sea_lake.update(range(nums[0], nums[1]+1))
        else:
            sea_lake.update(nums)
    # 禁制 = 全部陆地（全图 - 海/湖） - 保留（含无头衔无历史孤儿省份，避免游戏内异常显示）
    impass = sorted(all_ids - sea_lake - kept_prov)
    print(f"    禁制省份: {len(impass)}（全图 {len(all_ids)} - 海/湖 {len(sea_lake)} - 保留 {len(kept_prov)}）")
    def fmt_ranges(ids):
        lines = []
        i, n = 0, len(ids)
        singles = []
        def flush():
            while singles:
                lines.append("impassable_mountains = LIST { " + " ".join(map(str, singles[:20])) + " }")
                del singles[:20]
        while i < n:
            j = i
            while j+1 < n and ids[j+1] == ids[j] + 1:
                j += 1
            if j - i >= 4:
                flush()
                lines.append(f"impassable_mountains = RANGE {{ {ids[i]} {ids[j]} }}")
                i = j + 1
            else:
                singles.extend(ids[i:j+1])
                i = j + 1
        flush()
        return lines
    tmpl_path = os.path.join(EA, "map_data", "default.map")
    if not os.path.exists(tmpl_path):
        tmpl_path = os.path.join(GAME, "map_data", "default.map")
    tmpl = read(tmpl_path)
    if "#未恢复地区荒漠" in tmpl:
        head, _, _ = tmpl.partition("#未恢复地区荒漠")
    else:
        i = tmpl.find("impassable")
        head = tmpl[:i] if i > 0 else tmpl
    out = head + "#未恢复地区荒漠（聚焦东亚：区域外陆地全部禁制）\n" + \
          "\n".join(fmt_ranges(impass)) + "\n"
    write(os.path.join(EA, "map_data", "default.map"), out)

def step_framework():
    print("[7/9] 框架空壳 10_world_framework.txt")
    keep = set()
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        if os.path.basename(f) == "10_world_framework.txt":
            continue
        keep |= set(re.findall(r'(?m)^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', read(f)))
    TITLE_RE = r'([a-z]+_[a-zA-Z0-9_\-]+)'
    def shell_block(body):
        """递归保留 e/k/d 结构，剔除 c_/b_ 与 capital 引用"""
        out_lines = []
        child_pos = 0
        children = list(re.finditer(r'^\s*(%s)\s*=\s*\{' % TITLE_RE, body, re.M))
        idx = 0
        while idx < len(children):
            m = children[idx]
            out_lines.append(body[child_pos:m.start()])
            name = m.group(1)
            cbody, end = find_block(body, m.end()-1)
            if not name.startswith(("c_", "b_")):
                inner = shell_block(cbody)
                out_lines.append(f"{name} = {{\n{inner.rstrip()}\n}}\n")
            child_pos = end + 1
            idx += 1
            while idx < len(children) and children[idx].start() <= end:
                idx += 1
        out_lines.append(body[child_pos:])
        res = "".join(out_lines)
        return re.sub(r'(?m)^\s*capital\s*=\s*c_[^\n]*\n', '', res)
    out_parts = []
    for vf in sorted(glob.glob(os.path.join(GAME_LT, "*.txt"))):
        if vf.endswith(".info"):
            continue
        txt = read(vf)
        items = []
        for m in re.finditer(r'^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', txt, re.M):
            body, end = find_block(txt, m.end()-1)
            items.append((m.start(), m.group(1), body, end))
        items.sort()
        last_end = -1
        for start, name, body, end in items:
            if start <= last_end:
                continue
            last_end = end
            if name in keep:
                continue
            if name.startswith("e_"):
                out_parts.append(f"{name} = {{\n}}\n")
            elif not name.startswith("c_"):
                s = shell_block(body)
                out_parts.append(f"{name} = {{\n{s.rstrip()}\n}}\n")
    with open(os.path.join(EA_LT, "10_world_framework.txt"), "w",
              encoding="utf-8-sig", newline="\n") as f:
        f.write("@always_primary_score = 1000\n"
                "@better_than_the_alternatives_score = 50\n"
                "@correct_culture_primary_score = 100\n"
                "@never_primary_score = -1000\n\n"
                "# 区域外头衔框架(帝国纯空壳, 无王国/公国/伯爵领) — 供原版脚本引用解析\n\n")
        f.write("\n".join(out_parts))
    print(f"    框架完成: {len(out_parts)} 个空壳块")

def step_titles():
    print("[8/9] titles 历史裁剪")
    defined = set()
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        defined |= set(re.findall(r'(?m)^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', read(f)))
    REF_LINE = re.compile(
        r'^\s*(?:capital\s*=\s*|set_capital_county\s*=\s*title:|'
        r'liege\s*=\s*|de_jure_liege\s*=\s*|set_de_jure_liege_title\s*=\s*title:|'
        r'suzerain\s*=\s*)'
        r'"?([a-z]+_[a-zA-Z0-9_\-]+)"?', re.M)
    def strip_bad_refs(body):
        # 未定义引用只删前缀（保留行尾括号/注释，防止原版 `liege = X }` 同行的 } 丢失）
        return REF_LINE.sub(lambda m: "" if m.group(1) not in defined else m.group(0), body)
    def strip_comments(txt):
        out = []
        for line in txt.split("\n"):
            in_q = False
            cut = None
            for i, ch in enumerate(line):
                if ch == '"':
                    in_q = not in_q
                elif ch == '#' and not in_q:
                    cut = i
                    break
            out.append(line[:cut] if cut is not None else line)
        return "\n".join(out)
    def process_file(path):
        txt = strip_comments(read(path))
        items = []
        for m in re.finditer(r'^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', txt, re.M):
            body, end = find_block(txt, m.end()-1)
            items.append((m.start(), m.group(1), body, end))
        items.sort()
        parts = []
        last_end = -1
        for start, name, body, end in items:
            if start <= last_end:
                continue
            last_end = end
            if name not in defined:
                continue
            parts.append(f"{name} = {{\n{strip_bad_refs(body).rstrip()}\n}}\n")
        return "\n".join(parts).rstrip() + "\n"
    dst = os.path.join(EA, "history", "titles")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(GAME, "history", "titles"), dst)
    for f in sorted(glob.glob(os.path.join(dst, "*.txt"))):
        write(f, process_file(f))
    # 自建帝国最小历史
    for emp in NEW_EMPIRES:
        write(os.path.join(dst, f"00_{emp['name'][2:]}.txt"),
              f"{emp['name']} = {{\n\t867.1.1 = {{ }}\n}}\n")
    # 删除指定历史文件（防止被删头衔的幽灵持有者）
    for f in TITLES_DROP:
        fp = os.path.join(dst, f + ".txt")
        if os.path.exists(fp):
            os.remove(fp)
            print(f"    已删除历史 {f}.txt")
    print("    titles 裁剪完成")

def step_bookmarks():
    print("[9/9] 书签/组/挑战角色")
    bm_src = read(os.path.join(GAME, "common", "bookmarks", "bookmarks", "00_bookmarks.txt"))
    def extract(name):
        m = re.search(r'(%s\s*=\s*\{)' % name, bm_src)
        if not m:
            raise SystemExit(f"!! 书签 {name} 不存在")
        depth = 0
        i = m.end() - 1
        n = len(bm_src)
        while i < n:
            c = bm_src[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return bm_src[m.start():i+1]
            i += 1
        raise SystemExit(f"!! 书签 {name} 括号失衡")
    def drop_char_block(text, anchor):
        m = re.search(r'#\s*[^\n]*%s[^\n]*\n' % anchor, text)
        if not m:
            return text, False
        cm = re.search(r'character\s*=\s*\{', text[m.end():])
        if not cm:
            return text, False
        start = m.start()
        open_pos = m.end() + cm.end() - 1
        depth = 0
        i = open_pos
        n = len(text)
        while i < n:
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[:start] + text[i+1:], True
            i += 1
        return text, False
    parts = ["# 聚焦东亚书签\n"]
    for name in BOOKMARKS_KEEP:
        block = extract(name)
        for anchor in BOOKMARK_DROP_CHARS:
            block, ok = drop_char_block(block, anchor)
            if ok:
                print(f"    {name} 删除角色 {anchor}")
        if name == DEFAULT_BOOKMARK and "test_default" not in block:
            first = block.find('{') + 1
            block = block[:first] + "\n\ttest_default = yes" + block[first:]
            print(f"    {name} 设为默认剧本 (test_default)")
        parts.append(block + "\n")
    write(os.path.join(EA, "common", "bookmarks", "bookmarks", "00_bookmarks.txt"), "".join(parts))
    # groups
    t = read(os.path.join(GAME, "common", "bookmarks", "groups", "00_bookmark_groups.txt"))
    kept = []
    for gm in re.finditer(r'(bm_group_[a-z0-9_]+\s*=\s*\{)', t):
        depth = 0
        i = gm.end() - 1
        n = len(t)
        while i < n:
            c = t[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        gname = gm.group(1).split()[0]
        if gname in GROUPS_KEEP:
            kept.append(t[gm.start():i+1])
    write(os.path.join(EA, "common", "bookmarks", "groups", "00_bookmark_groups.txt"), "\n".join(kept) + "\n")
    # challenge_characters 空化
    cc = os.path.join(EA, "common", "bookmarks", "challenge_characters")
    mkdirs(cc)
    for f in os.listdir(os.path.join(GAME, "common", "bookmarks", "challenge_characters")):
        write(os.path.join(cc, f), "")

def step_localization():
    print("[+] 自建帝国本地化")
    if not NEW_EMPIRES:
        print("    无自建帝国，跳过")
        return
    mkdirs(os.path.join(EA, "localization", "english"))
    mkdirs(os.path.join(EA, "localization", "simp_chinese"))
    en = "l_english:\n"
    zh = "l_simp_chinese:\n"
    for emp in NEW_EMPIRES:
        en += f" {emp['name']}: \"{emp['en']}\"\n {emp['name']}_adj: \"{emp['en_adj']}\"\n"
        zh += f" {emp['name']}: \"{emp['zh']}\"\n {emp['name']}_adj: \"{emp['zh_adj']}\"\n"
    write(os.path.join(EA, "localization", "english", "new_titles_l_english.yml"), en)
    write(os.path.join(EA, "localization", "simp_chinese", "new_titles_l_simp_chinese.yml"), zh)
    print("    本地化完成")

def verify():
    print("[*] 校验括号平衡")
    for f in glob.glob(os.path.join(EA_LT, "*.txt")):
        t = read(f)
        d = t.count('{') - t.count('}')
        if d != 0:
            raise SystemExit(f"!! {os.path.basename(f)} 括号失衡 {d}")
    for f in glob.glob(os.path.join(EA, "history", "titles", "*.txt")):
        t = read(f)
        d = t.count('{') - t.count('}')
        if d != 0:
            raise SystemExit(f"!! {os.path.basename(f)} 括号失衡 {d}")
    print("    全部平衡")

def report():
    """树状输出保留的霸权/帝国 → 王国 → 公国（伯爵领/男爵领数量汇总）
    写入 mod 根目录《保留区域报告.txt》：顶部简略信息，下方详细树状。"""
    import datetime
    def parse(block_text):
        """解析块内全部子头衔，返回 [(name, block, children)]"""
        items = []
        for m in re.finditer(r'(?m)^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', block_text):
            if not m.group(1).startswith(("e_", "h_", "k_", "d_", "c_", "b_")):
                continue
            body, end = find_block(block_text, m.end()-1)
            items.append((m.start(), m.group(1), body, end))
        items.sort()
        tree = []
        last_end = -1
        for start, name, body, end in items:
            if start <= last_end:
                continue
            last_end = end
            tree.append((name, block_text[start:end+1], parse(body)))
        return tree
    top = []
    for f in sorted(glob.glob(os.path.join(EA_LT, "*.txt"))):
        if os.path.basename(f) == "10_world_framework.txt":
            continue
        txt = read(f)
        items = []
        for m in re.finditer(r'^\s*([a-z]+_[a-zA-Z0-9_\-]+)\s*=\s*\{', txt, re.M):
            if not m.group(1).startswith(("e_", "h_", "k_", "d_", "c_", "b_")):
                continue
            body, end = find_block(txt, m.end()-1)
            items.append((m.start(), m.group(1), body, end))
        items.sort()
        last_end = -1
        for start, name, body, end in items:
            if start <= last_end:
                continue
            last_end = end
            if name[0] in ("e", "h"):
                top.append((name, txt[start:end+1], parse(body)))
    def provs(block):
        return len(re.findall(r'province\s*=\s*\d+', block))
    def cnt(block, pfx):
        return len(re.findall(r'(?m)^\s*%s[a-zA-Z0-9_\-\x27]+\s*=\s*\{' % pfx, block))
    tier = {"h": "霸权", "e": "帝国", "k": "王国", "d": "公国",
            "c": "伯爵领", "b": "男爵领"}
    total = sum(provs(b) for _, b, _ in top)
    # 禁制省份数（读 default.map）
    imp = 0
    try:
        dm = read(os.path.join(EA, "map_data", "default.map"))
        for m in re.finditer(r'impassable_mountains = (RANGE|LIST) \{ ([^}]+) \}', dm):
            nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
            if m.group(1) == 'RANGE' and len(nums) == 2:
                imp += nums[1] - nums[0] + 1
            else:
                imp += len(nums)
    except Exception:
        pass
    # 层级统计
    stats = {"h": 0, "e": 0, "k": 0, "d": 0, "c": 0, "b": 0}
    def count_tree(tree):
        for name, block, children in tree:
            stats[name[0]] += 1
            count_tree(children)
    for _, _, tree in top:
        count_tree(tree)
    # ---------- 简略信息 ----------
    L = []
    L.append("《聚焦地中海》保留区域报告")
    L.append("生成时间: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    L.append("")
    L.append(f"地块总数: {total} | 禁制省份: {imp}")
    L.append(f"顶级霸权/帝国: {len(top)}")
    L.append("")
    L.append("【简略汇总】（按地块数排序）")
    def kingdom_lines(tree, prefix="        "):
        """顶级下两级展开：子帝国 → 王国"""
        lines = []
        for name, block, children in tree:
            if name[0] == "k":
                lines.append(f"{prefix}k_{name[2:]} (王国) {provs(block)} 地块")
            elif name[0] == "e":
                kl = kingdom_lines(children, prefix + "    ")
                if kl:
                    lines.append(f"{prefix}{name[2:]} (帝国) {provs(block)} 地块")
                    lines.extend(kl)
        return lines
    for i, (name, block, tree) in enumerate(
            sorted(top, key=lambda x: -provs(x[1])), 1):
        L.append(f"  {i:2d}. {name:<20s} {tier[name[0]]}  {provs(block):5d} 地块")
        L.extend(kingdom_lines(tree))
    L.append("")
    L.append(f"层级统计: 霸权 {stats['h']} | 帝国 {stats['e']} | "
             f"王国 {stats['k']} | 公国 {stats['d']} | "
             f"伯爵领 {stats['c']} | 男爵领 {stats['b']}")
    L.append("")
    # ---------- 详细信息 ----------
    L.append("【详细信息】")
    L.append("")
    def render(tree, prefix="", depth=0):
        for i, (name, block, children) in enumerate(tree):
            last = i == len(tree) - 1
            mark = "└─ " if last else "├─ "
            p = provs(block)
            tag = f"【{tier[name[0]]}】" if name[0] in ("e", "h") else f"({tier[name[0]]})"
            extra = ""
            if depth == 1 and name[0] not in ("e", "h"):
                extra = f"  +{cnt(block, 'c_')}伯爵领/{cnt(block, 'b_')}男爵"
            L.append(f"{prefix}{mark}{name} {tag} ({p} 地块){extra}")
            if children and depth < 2:
                render(children, prefix + ("    " if last else "│   "), depth + 1)
    for name, block, tree in sorted(top, key=lambda x: -provs(x[1])):
        L.append(f"◆ {name} 【{tier[name[0]]}】 ({provs(block)} 地块)")
        render(tree, "", 0)
        L.append("")
    out_path = os.path.join(EA, "保留区域报告.txt")
    write(out_path, "\n".join(L))
    print(f"\n[报告] 已写入《保留区域报告.txt》  |  地块总数: {total} | "
          f"顶级霸权/帝国: {len(top)} | 禁制省份: {imp}")

def main():
    print(f"《聚焦地中海》构建开始（mod 目录: {EA}）")
    step_copy()
    step_new_empires()
    step_extract()
    step_move_remove()
    step_capital()
    step_map()
    step_framework()
    step_titles()
    step_bookmarks()
    step_localization()
    verify()
    report()
    print("构建完成")

if __name__ == "__main__":
    main()
