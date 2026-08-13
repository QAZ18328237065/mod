# 东亚 867 全文化 × 特殊兵种矩阵（分析用基线 v1.0）

> 用途：按**单独文化**重做特殊兵种的前置盘点。
> 范围：中国 / 日本 / 朝鲜半岛 / 东北（满洲）/ 西藏。游牧文化（蒙古高原、契丹、室韦、吐谷浑、回鹘系）已按决定**全部排除**。
> 数据来源：原版 culture 文件、history/provinces 867.1.1 生效文化、现有 mod 4 条兵种线、原版 TGP/MPO 兵种。

## 0. 图例

- **现状兵种**：该文化目前能招募的 mod 特殊兵种（按 can_recruit 支柱判定）+ 原版特殊兵种（按传统参数解锁）。
- **状态**：`已覆盖`（mod 有兵种）/ `盲区`（原判定支柱与实际支柱不符，招不到）/ `无`（完全无特殊兵种）。

## 1. 总览矩阵

| 文化 | key | 支柱 | 区域 | 867 省 | 现状 mod 兵种 | 原版兵种 | 状态 |
|------|-----|------|------|--------|--------------|----------|------|
| 汉 | han | chinese | 中原 | 241 | 跳荡/长枪都/飞骑/射生军 | 斩马刀队、黑甲骑、神臂弓 | 已覆盖 |
| 彝 | yi | chinese | 云贵川 | 26 | 跳荡/长枪都/飞骑/射生军 | — | 已覆盖* |
| 白 | bai | chinese | 云南 | 11 | 跳荡/长枪都/飞骑/射生军 | — | 已覆盖* |
| 党项 | tangut | qiangic | 陕北 | 54 | 跳荡/长枪都/飞骑/射生军 | — | 已覆盖* |
| 羌 | qiang | qiangic | 川西/陇南 | 62 | 跳荡/长枪都/飞骑/射生军 | — | 已覆盖* |
| 黎 | hlai | **tai** | 海南 | 4 | **无（支柱不符）** | — | **盲区** |
| 大和 | japanese | japonic | 本州/九州 | 66 | 防人弓队/马寮轻骑/健児队 | 武士、骑侍、日本弓骑 | 已覆盖 |
| 琉球 | ryukyuan | japonic | 琉球群岛 | 2 | 防人弓队/马寮轻骑/健児队 | — | 已覆盖* |
| 虾夷 | emishi | **ainuic** | 本州东北 | 6 | **无（支柱不符）** | 虾夷骑手（传统解锁） | 盲区 |
| 阿伊努 | ainu | **ainuic** | 北海道 | 5 | **无（支柱不符）** | — | 盲区 |
| 高丽 | goryeo | korean | 朝鲜半岛 | — | 花郎/高句丽弓骑/誓幢军 | — | 已覆盖 |
| 新罗 | silla | korean | 庆州 | 12 | 花郎/高句丽弓骑/誓幢军 | — | 已覆盖 |
| 百济 | baekje | buyeo | 半岛西南 | — | 花郎/高句丽弓骑/誓幢军 | — | 已覆盖* |
| 高句丽 | goguryeo | buyeo | 半岛北部 | 24 | 花郎/高句丽弓骑/誓幢军 | — | 已覆盖* |
| 渤海 | balhae | buyeo | 东北南部 | 19 | 花郎/高句丽弓骑/誓幢军 | — | 已覆盖* |
| 吐蕃 | bodpa | tibetan | 卫藏 | 221 | 雪域弓手/深山伏戎 | — | 已覆盖 |
| 象雄 | zhangzhung | tibetan | 阿里 | 63 | 雪域弓手/深山伏戎 | — | 已覆盖* |
| 苏毗 | sumpa | tibetan | 那曲/昌都 | 72 | 雪域弓手/深山伏戎 | — | 已覆盖* |
| 藏巴 | tsangpa | tibetan | 后藏 | 14 | 雪域弓手/深山伏戎 | — | 已覆盖* |
| 基拉蒂 | kirati | tibetan | 藏南 | 9 | 雪域弓手/深山伏戎 | — | 已覆盖* |
| 珞门 | lhomon | tibetan | 藏南/不丹 | 29 | 雪域弓手/深山伏戎 | — | 已覆盖* |
| 靺鞨 | mohe | tungusic | 松嫩/黑龙江 | 33 | **无** | — | **无** |
| 女真 | jurchen | tungusic | 营州/渤海北境 | 7 | **无** | — | **无** |
| 沙陀 | shatuo | turkic | 雁北/河东 | 11 | **无** | — | **无** |
| 苗 | hmong | hmongic | 黔湘桂 | 17 | **无** | — | **无** |
| 瑶 | yao | hmongic | 湘桂粤 | 20 | **无** | — | **无** |
| 布依壮 | bouxcuengh | tai | 广西/贵州 | 27 | **无** | — | **无** |
| 傣 | tai | tai | 云南南部 | 9 | **无** | — | **无** |
| 越 | viet | viet | 红河平原 | 9 | **无** | — | **无** |

\* = 经支柱间接覆盖（非文化专属，共享同线兵种）。未标 \* 的为该线核心文化。

## 2. 现状兵种 → 文化归属明细（按 mod 文件）

### 2.1 中国线 `zz_china_867_maa_types.txt`（can_recruit: heritage_chinese + heritage_qiangic）

| 兵种 | 类型 | 实际覆盖文化 | 备注 |
|------|------|-------------|------|
| 跳荡兵 tiaodang | 散兵 | han、yi、bai、tangut、qiang | 神策军跳荡 |
| 长枪都 changqiangdu | 枪兵 | 同上 5 文化 | 晚唐都军制 |
| 飞骑 feiji | 轻骑 | 同上 5 文化 | 羽林飞骑 → 已更名**神策游骑 shence_youqi**（飞骑为唐前期北衙禁军，867 已消亡；神策游弈骑为正解） |
| 射生军 sheshengjun | 弓骑 | 同上 5 文化 | 神策射生 |

**判定缺口**：`hlai`（heritage_tai）——4 个中国兵种全部招不到。

### 2.2 日本线 `99_japan_special_maa.txt`（can_recruit: heritage_japonic）

| 兵种 | 类型 | 实际覆盖文化 | 备注 |
|------|------|-------------|------|
| 防人弓队 japan_sakimori_archers | 弓兵 | japanese、ryukyuan | 西海道防人 |
| 马寮轻骑 japan_umaya_light_cavalry | 轻骑 | 同上 2 文化 | 律令马寮 |
| 健児队 kondei | 散兵 | 同上 2 文化 | 地方健児 |

**判定缺口**：`emishi`、`ainu`（heritage_ainuic）——3 个日本兵种全部招不到（emishi 只有原版虾夷骑手）。

### 2.3 韩国线 `zz_korea_maa_types.txt`（can_recruit: heritage_korean + heritage_buyeo）

| 兵种 | 类型 | 实际覆盖文化 | 备注 |
|------|------|-------------|------|
| 花郎 hwarang | 重步 | goryeo、silla、baekje、goguryeo、balhae | 新罗花郎徒 |
| 高句丽弓骑 goguryeo_horse_archers | 弓骑 | 同上 5 文化 | 高句丽骑射 |
| 誓幢军 sechang | 枪兵 | 同上 5 文化 | 九誓幢 |

**判定缺口**：无。半岛 5 文化全覆。

### 2.4 西藏线 `zz_tibet_maa_types.txt`（can_recruit: heritage_tibetan）

| 兵种 | 类型 | 实际覆盖文化 | 备注 |
|------|------|-------------|------|
| 雪域弓手 snowfield_archers | 弓兵 | 全部 6 文化 | 柳叶弓 |
| 深山伏戎 highland_ambushers | 散兵 | 全部 6 文化 | 山地伏击 |

**判定缺口**：无。卫藏/安多/阿里全覆。

### 2.5 原版特殊兵种（TGP 天赐之命，传统参数解锁，非本 mod）

| 兵种 | 解锁方式 | 绑定文化 |
|------|---------|---------|
| 斩马刀队 zhanmadao_infantry | 汉文化传统参数 | han |
| 黑甲骑 black_armor_cavalry | 同上 | han |
| 武士 samurai / 骑侍 mounted_samurai / 日本弓骑 | 武士道传统参数 | japanese |
| 虾夷骑手 emishi_horse_archers | 虾夷传统参数 | emishi |

## 3. 未覆盖文化待设计清单（13 个，含 3 盲区）

| 优先 | 文化 | 支柱 | 867 省 | 建议兵种方向（史实依据，待定稿） |
|------|------|------|--------|----------------------------------|
| P1 | mohe 靺鞨 | tungusic | 33 | 楛矢弓手（弓兵，楛矢石砮闻名，森林作战） |
| P1 | jurchen 女真 | tungusic | 7 | 铁鹞军雏形？（重步/甲骑，营州地区武化） |
| P1 | shatuo 沙陀 | turkic | 11 | 鸦儿军（轻骑/重骑，李克用沙陀铁骑） |
| P2 | viet 越 | viet | 9 | 交趾短弩手（弓兵，步兵阵） |
| P2 | tai 傣 | tai | 9 | 象阵（象兵线，傣族"控象之王"传统） |
| P2 | bouxcuengh 布依壮 | tai | 27 | 僚人藤甲兵（散兵，藤甲+毒弩） |
| P2 | hmong 苗 | hmongic | 17 | 苗弩手（弓兵，毒弩/山地伏击） |
| P2 | yao 瑶 | hmongic | 20 | 瑶山猎手（散兵） |
| P3 | hlai 黎 | tai（盲区） | 4 | 黎峒弓手（弓兵，海南峒民） |
| P3 | emishi 虾夷 | ainuic（盲区） | 6 | 已有原版虾夷骑手，可补 mod 强化或跳过 |
| P3 | ainu 阿伊努 | ainuic（盲区） | 5 | 阿伊努猎手（散兵） |
| — | hlai/bai 等已覆盖文化 | — | — | 按"单独文化"原则，yi/bai/tangut/qiang/ryukyuan/baekje/goguryeo/balhae/zhangzhung 等将各自拥有专属兵种（需逐文化设计） |

## 4. 重新设计约束（v3.1 待改）

1. **判定方式**：`can_recruit` 从支柱判定改为**逐文化判定** `culture = { this = culture:xxx }`（或 OR 多文化），确保 hlai/emishi/ainu 等支柱错位文化可被精确覆盖。
2. **位阶区间**：保持 N ∈ [60, 95]（v5.2 降档），中国 90-95 > 日本 85.5-88.1 > 韩国 80.5-83.5 > 东北 76-79 > 南诏 74-75.5 > bodpa 71.5-72.5；新增线按国情插位。
3. **原版已有兵种不重复**：han（斩马刀/黑甲骑）、japanese（武士/骑侍）、emishi（虾夷骑手）避免同质设计。
4. **地形权重**：新增文化按所在区域套用 v3.0 六区域权重（东北=forest/taiga 权重，南方=jungle/hills，越=东南亚系）。

## 5. 待确认问题

- [ ] 新增 10 文化的位阶区间定档（建议：东北 80-85、南方 75-82、日本盲区并入 89-96？）
- [ ] mohe/jurchen 共享 tungusic 还是逐文化？
- [ ] tai 傣象兵是否与南亚象兵（war_elephants）冲突？
- [ ] viet 是否纳入（越南属东南亚区划，但 k_viet 在 867 为中国南疆）
- [ ] emishi/ainu 是否纳入 mod（原版已有虾夷骑手覆盖 emishi）
