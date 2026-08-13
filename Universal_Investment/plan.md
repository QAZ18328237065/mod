# 天下置业 (Universal_Investment) — 无门槛投资建城玩法(有地领主·活动版)

> 版本: v3.0 实现稿(代码已全部落盘,待 Tiger 校验与游戏内测试) | 目标游戏: CK3 1.19.0.6 (EP3)
> 原版模板: `monument_expedition`(全图选点) + `activity_survey`(地图筛选) + 事件链 `ep3_laamp_decision_event.1130/1131`
> 设计原则: **无门槛、有代价、随处可投、收益闭环(仅年金一条链路)**
> 命名规范: 全部键以项目名 `universal_investment_` 为前缀;事件命名空间 `universal_investment`

---

## 1. 玩法概述

**有地领主**通过举办「投资考察」**活动**,在地图上直接点选任何符合条件的空男爵领
(自己领地/封臣领地/领主领地/外国领地),旅行过去实地开工。
无创新/好感/属性门槛。代价: **活动差旅费 50 金** + **阶梯建造成本** 400×2^(N-1)(封顶 12800)+ 建造期风险事件。
**开工后角色即可回家,建造与事件链全程不依赖人在场**。
建成后城堡归当地伯爵领持有者,玩家成为"股东",每年收取**年金(建造成本×10%,保底 10 金)**——唯一结算链路。
累计建成数解锁里程碑(3/5/10 座)。核心张力: 无法律保护,年金随时可能被拒付/没收。

---

## 2. 全流程时序(实现版)

```
[活动面板: 投资考察]
  → is_shown(有地领主+EP3) → can_start(基本条件)
  → 旅行规划: 全图列出符合 is_location_valid 的男爵领(province_filter=all,图标+悬浮提示含风险标注)
  → 选点 → 付差旅费 50 → 自动旅行
  → 到达 → on_phase_active → 开工事件 0001(1 个月内自动结束活动回家)
       A 开工: 扣阶梯成本 → begin_create_holding → 记录(pending 列表+barony 4 变量) → 开监控链 → 持有者好感-10
       B 反悔: 只亏差旅费
  → [建造监控链 0011 月度自循环,root 存活即有]
       every_in_list pending 逐笔: 完工→结算 | 取消→停跟 | 在建→月数+1,≥3 掷风险
       风险: 敲诈(0002)/事故(0003),玩家弹窗,AI 自动付账
  → 完工结算: 送建筑组(laamp_city_builder_construction_effect×5) → 入年金名单 → +100 威望
       → 完工通知(0004,仅玩家) → 里程碑检查(0008/0009/0010)
  → [每年] yearly_playable_pulse → 0005(隐藏)遍历年金名单:
       被毁/缺失→作废 | 持有者=自己→免税(保留,封出自动转年金) | 易主→认账判定(50%+好感)
       认账→付款 | 拒付→玩家弹 0006 交涉(AI 自动续约) | 正常→付款
       pay_short_term_gold 从持有者金库扣钱(不足自动分月补扣)
       → 年度报告(0007,仅玩家)
```

---

## 3. 文件清单(全部已实现 ✅)

```
Universal_Investment/
├── descriptor.mod / Universal_Investment.mod                  ✅
├── plan.md                                                     ✅ 本文件
├── common/
│   ├── activities/activity_types/zzz_universal_investment_survey_activity.txt  ✅ 活动定义
│   ├── on_action/zzz_universal_investment_on_actions.txt       ✅ yearly_playable_pulse 追加
│   ├── opinion_modifiers/zzz_universal_investment_opinion_modifiers.txt  ✅ 6 个好感修正
│   ├── scripted_effects/zzz_universal_investment_effects.txt   ✅ 14 个效果(开工/监控/结算/年金/交涉/风险)
│   ├── script_values/zzz_universal_investment_values.txt       ✅ 12 个数值(成本阶梯/概率/费用)
│   └── (无 scripted_triggers: 实现后确认无必要,省略)
├── events/universal_investment/zzz_universal_investment_events.txt  ✅ 11 个事件(0001~0011)
└── localization/
    ├── english/universal_investment_l_english.yml              ✅
    └── simp_chinese/universal_investment_l_simp_chinese.yml    ✅
```

### 事件表
| ID | 类型 | 说明 |
|---|---|---|
| 0001 | 弹窗 | 开工确认(到达后) |
| 0002 | 弹窗 | 领主敲诈(付补偿/强硬拒绝/接受没收) |
| 0003 | 弹窗 | 工地事故(修复/放弃) |
| 0004 | 弹窗 | 完工通知(仅玩家) |
| 0005 | 隐藏 | 年金年度处理(玩家+AI) |
| 0006 | 弹窗 | 赖账交涉(谈判/贿赂/威胁/放弃) |
| 0007 | 弹窗 | 年度投资报告(仅玩家) |
| 0008/0009/0010 | 弹窗 | 里程碑 3/5/10 座 |
| 0011 | 隐藏 | 建造监控链(月度自循环) |

### 存储设计(全部 character 级 + barony 级)
- 玩家变量: `start_count`(成本阶梯)/ `built_count`(里程碑)/ `watcher_active`(监控链开关)/ `milestone_3/5/10`
- 玩家列表: `pending`(在建)/ `portfolio`(年金)
- 玩家待处理变量: `risk_target` / `dispute_target` / `notification_target`(各带 has_variable 守卫,同一时间仅一个待处理事件,防变量互抢)
- barony 变量: `pending`(在跟状态)/ `owner`(投资者)/ `holder`(建时持有者)/ `annuity`(年金基数=该笔建造成本)/ `active`(年金有效)/ `cancelled`(没收)/ `dispute`(结怨)/ `risk_rolled`(风险已掷)/ `pending_months`(在建月数)
- 列表随角色死亡自然消失 → 死亡自动清盘,无泄漏

---

## 4. 实现偏差记录(相对 v2.1 计划)

| # | 计划 | 实现 | 原因 |
|---|---|---|---|
| 1 | every_in_variable_list / remove_from_variable_list | `every_in_list = { variable = X }` + 状态 flag 代替删除 | 原版 1.19 无此命令(全游戏 grep 0 次),借原版借贷系统语法(00_scripted_effects.txt:44, holy_order.0206) |
| 2 | 每笔投资独立完工自循环(scope 传递) | 每角色**单条监控链** 0011,列表驱动 | 多链并存时 scope:province 同名传递有碰撞风险;监控链无 scope 依赖,确定性最强 |
| 3 | 风险事件按开工排期 months={3 5} | 并入监控链: pending_months ≥ 3 时掷骰 | 同上,消除排期事件 scope 传递 |
| 4 | can_start 检查"存在 ≥1 合法地点" | 省略 | 原版无 any_barony/any_province 全局遍历触发(全游戏 grep 0 次);靠 is_location_valid 地图筛选兜底 |
| 5 | D7(自己领地封出转年金)需单独处理 | 自己领地建成**也入年金名单**,年度检查 holder=自己 时免税不付款 | 封出后 holder 变更 → 认账判定自动转年金,天然实现 D7 |
| 6 | scripted_triggers 文件 | 省略 | 实现后确认无必要(判定全部内联/script_values) |
| 7 | 反悔项 0001.b 无触发 | 同计划 | 无 |
| 8 | on_action 合并疑虑 | 已验证安全: 原版 yearly_playable_pulse 同键名多次定义(three_year_playable_pulse ×2, yearly_on_actions.txt:1975/2915),引擎合并 events 列表 | 追加 `events = { universal_investment.0005 }` 不覆盖原版 effect |

---

## 5. 关键机制对照(实现引用)

| 机制 | 实现位置 | 原版依据 |
|---|---|---|
| 全图选点 | 活动 province_filter = all | monument_expedition.txt:95 |
| 地图筛选 | is_location_valid(root=省) | _activity_type.info:111~117, inspection.txt:98 |
| 建造开工 | begin_create_holding = { type = castle_holding } | ep3_laamp_decision_events.txt:20943 |
| 送建筑组 | laamp_city_builder_construction_effect ×5(FLAG/BUILDING) | 同文件:21034~21055(原版 1131 完工段参数) |
| 年金转账 | pay_short_term_gold = { target = root gold = {...} } | prelude_events.txt:143(原版借贷机制,不足自动分月补扣) |
| 列表存取 | add_to_variable_list / every_in_list / any_in_list | 00_scripted_effects.txt:44 / holy_order_events.txt:286 |
| 变量增减 | set_variable / change_variable = { name add = 1 } | 00_scripted_effects.txt:40 / holy_order_events.txt:296 |
| 好感修正 | add_opinion = { target modifier } + opinion_modifiers 文件 | festival.txt:267 / 00_activity_feast_opinions.txt |
| 意图复用 | survey_overseer_intent / survey_learning_intent_guest | survey_intents.txt:3/21 |
| 事件 scope | root=玩家,目标经变量传递(risk_target 等) | 无 scope 传递,确定性 |

---

## 6. 待验证清单(写码中已解决 ⏳→✅)

- [x] 列表遍历/移除语法 → `every_in_list = { variable = X }`(原版借贷系统)
- [x] `change_variable` 语法 → `change_variable = { name = X add = 1 }`
- [x] `add_to_variable_list` target 语法 → `{ name = X target = scope }`
- [x] `any_barony`/`any_province` 是否存在 → **不存在**,放弃全局遍历检查
- [x] on_action 合并行为 → 原版同键多次定义可合并
- [x] 活动 loc 键格式 → `<key>` / `_desc` / `_host_desc` / `_province_desc` / `_conclusion_desc` / `phase_<key>`
- [x] `nick_the_city_builder` 存在(01_bp2_nicknames.txt:1)
- [x] `add_opinion` 语法(target+modifier)
- [x] `add_character_modifier`/`give_nickname` 语法
- [x] script_value 作用域引用(root./scope:X.var:Y)—— 00_activity_values.txt:749/834
- [ ] **游戏内实测**(未做): 活动选点/到达开工/回家后完工/易主认账/死亡清盘
- [ ] **Tiger 校验**(未做)
- [ ] `laamp_city_builder_construction_effect` 是否依赖前置 flag(读了 1131 调用方式,但 effect 内部未细读,实测确认)
- [ ] `progress_activity_phase_after = { months = 1 }` 生效(活动 1 个月自动结束回家)
- [ ] 隐藏事件(0005/0011)无 option 的合法性(原版 holy_order.0206 同款,应安全)

---

## 7. 设计决策最终态(全部采用计划默认)

| 编号 | 决策 | 采用 |
|---|---|---|
| D2 | 投资目标归属 | 全允许,自己领地免年金(建成也入名单,holder=自己时免税) |
| D3 | 无主荒地 | 禁止(is_location_valid 要求 county.holder 存在) |
| D4 | 好感副作用 | -10(自己领地免) |
| D6 | 失地后年金 | 停发(yearly 触发 is_landed 拦截) |
| D7 | 自己领地封出后 | 自动转年金(名单保留+免税设计天然实现) |
| D8 | 成本计数口径 | 开工即计(start_count) |
| D9 | 年金回报率 | 成本×10%/年,保底 10,回收期约 10 年 |
| D10 | 活动差旅费 | 50 金 |
| D11 | 活动冷却 | 无 |

---

## 8. 剩余工作

1. ~~Tiger 校验~~ ✅ 已通过(fatal 0 / error 0 / warning 0,ck3-tiger v1.19.0,conf 过滤 2 类原版实证误报)
2. **游戏内测试四场景**(未做): 旅行选点/到达开工/回家后完工/易主认账 + 死亡清盘 + AI 行为
3. 按实测结果修 bug 后,可考虑 v2 扩展(投资风格选择/视察交互/联合投资)
