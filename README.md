# 职途 JobReady · 全流程求职辅助助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validate Skill](https://github.com/kyoucc/jobready-career-assistant/actions/workflows/validate.yml/badge.svg)](https://github.com/kyoucc/jobready-career-assistant/actions/workflows/validate.yml)
[![WorkBuddy Skill](https://img.shields.io/badge/WorkBuddy-Skill-blue.svg)](https://www.workbuddy.cn)

---

## 这是什么

一个面向**校招 / 实习 / 初入职场**的全流程求职辅助技能包，为 WorkBuddy AI 提供从投递到入职的完整方法论。

它不是「AI 帮你写简历」这类泛泛的提示词集合，而是把 HR 与猎头的实际筛选逻辑拆成了可执行的流程、评分卡和话术模板 —— 覆盖 7 大能力、8 份方法论文档、3 份输出骨架、2 个可执行脚本。

## 解决什么问题

| 求职中的真实痛点 | 本技能的做法 |
|---|---|
| 简历写成了岗位说明书，全是「负责 XX」没有结果 | STAR 改写公式 + 量化补全引导，逐段标注修改原因 |
| 不知道 JD 到底想要什么，投了没回音 | 隐藏软要求反推表（从措辞推断真实工作强度与团队状态） |
| 面试答完不知道差在哪，只能感觉「好像没答好」 | 10 分制评分卡，5 个维度权重明确，逐题指出「哪句话让分数掉了」 |
| 拿到多个 offer 只比月薪 | 七维对比 + **实际时薪**换算（把加班和公积金算进去） |
| 谈薪不知道能谈什么、怎么开口 | 三阶段话术模板，并说明校招 offer 里哪些项可谈、哪些是标准化定级 |
| 搜到的薪资数据是几年前的 | 强制现场检索，输出必须标注来源、日期、样本范围 |

## 能力一览

| # | 能力 | 产出物 |
|---|---|---|
| 1 | **简历优化** | 整体评价 + 逐段改写后的完整简历 + 加分项建议 |
| 2 | **JD 拆解** | 硬性要求 / 隐藏软要求 / 薪资与城市性价比 / 差距分析 / 面试考点预测 |
| 3 | **面试模拟** | 5 道高频题 + 逐题 10 分制评分 + 满分回答改写 + 复盘报告 |
| 4 | **求职文书** | 求职信、感谢信、Offer 接受函、拒信、咨询邮件、实习证明 |
| 5 | **Offer 对比与谈判** | 七维对比表 + 换算结果 + 初谈/还价/收尾三阶段话术 |
| 6 | **行业与薪资参考** | 白菜价 / SP / SSP 分档区间 + 晋升双通道 + 转行风险 |
| 7 | **职场新人指南** | 入职清单、试用期避坑、周报模板、向上沟通话术、跨部门协作 |

## 安装

### 方式一：一键安装（推荐）

**macOS / Linux / Git Bash**

```bash
git clone https://github.com/kyoucc/jobready-career-assistant.git
cd jobready-career-assistant
bash install.sh
```

**Windows PowerShell**

```powershell
git clone https://github.com/kyoucc/jobready-career-assistant.git
cd jobready-career-assistant
powershell -ExecutionPolicy Bypass -File install.ps1
```

脚本会把 `SKILL.md`、`references/`、`assets/`、`scripts/`、`examples/` 复制到
`~/.workbuddy-ai/skills/jobready-career-assistant/`，已存在时会先询问是否覆盖。

### 方式二：手动安装

```bash
git clone https://github.com/kyoucc/jobready-career-assistant.git \
  ~/.workbuddy-ai/skills/jobready-career-assistant
```

仓库根目录即技能根目录，直接克隆到技能目录即可生效。

### 方式三：下载 zip

从 [Releases](https://github.com/kyoucc/jobready-career-assistant/releases) 下载后解压到
`~/.workbuddy-ai/skills/` 下，确保目录名为 `jobready-career-assistant`。

> 安装后若未立即生效，重启 WorkBuddy 客户端即可。

## 使用

直接用自然语言描述需求即可触发，无需记命令：

```
帮我改一下简历，我投的是 CV 算法工程师实习
```

```
拆一下这个 JD，看看我够不够格：【粘贴 JD】
```

```
模拟一次技术面，目标岗位是 CV 算法实习，重点问项目
```

```
A 公司月薪 22k 12 薪无年终奖保证，B 公司 20k 14 薪公积金按最低基数，怎么选？
```

也可以显式点名：

```
用职途 JobReady 帮我准备一下明天上午的 HR 面
```

**全流程陪跑**：如果你希望系统性地准备，可以让它按
`JD 拆解 → 简历改写 → 求职文书 → 模拟面试 → 复盘打磨 → Offer 对比 → 谈薪 → 入职准备`
的顺序推进。

## 脚本

### `scripts/offer_calc.py` — Offer 总包计算器

把「只比月薪」升级为「比年度现金 + 公积金 + 实际时薪」。纯标准库，无第三方依赖，Python 3.8+。

```bash
python scripts/offer_calc.py --demo                         # 查看示例输入与输出
python scripts/offer_calc.py offers.json                    # 传入 JSON 输入
python scripts/offer_calc.py offers.json --format markdown  # 输出 Markdown 表格
python scripts/offer_calc.py offers.json --json-out r.json  # 结果另存为 JSON
```

输出指标：年度现金（区分**保证部分**与**浮动部分**）、股票年均价值、公积金双边年收益、
月度到手现金、月度可支配余额、月度综合收益、年工作小时数、**实际时薪**、首年试用期折损。

脚本会自动给出风险提示，例如「年终奖未写入合同，已计入浮动部分」「公积金基数与月薪不一致」
「周工时高于法定标准工时」。

> 社保与个税采用比例估算，非逐级累进精算。结果用于横向比较，不等同于实际到手金额。

### `scripts/validate_skill.py` — 格式校验器

自包含，不依赖 WorkBuddy 内置脚本，可在任意环境运行：

```bash
python scripts/validate_skill.py .
```

校验 SKILL.md 是否存在、frontmatter 是否完整可解析、`name` 是否与目录名一致、
description 长度是否合理、所有引用路径是否真实存在、有无遗留占位符。

## 目录结构

```
jobready-career-assistant/
├── SKILL.md                          # 技能主控文件：角色定位 + P0 规则 + 能力路由表
├── references/                       # 方法论（按需加载，避免主文件臃肿）
│   ├── 01-resume-optimization.md     # STAR 改写、量化补全、ATS 关键词矩阵
│   ├── 02-jd-analysis.md             # 隐藏软要求反推表、差距分级、JD 质量诊断
│   ├── 03-interview-simulation.md    # 10 分制评分卡、行为/HR/压力面题库
│   ├── 04-job-documents.md           # 6 类求职文书全文范例
│   ├── 05-offer-negotiation.md       # 七维对比算法、三阶段谈判话术
│   ├── 06-salary-benchmark.md        # 分档定义、检索规范、降级路径
│   ├── 07-newcomer-guide.md          # 入职清单、周报模板、向上沟通
│   └── 08-tech-interview-bank.md     # 技术面题库（八股/手撕/项目深挖/CV）
├── assets/                           # 可直接填充的输出骨架
│   ├── resume-review-report.md
│   ├── interview-review-report.md
│   └── offer-comparison-table.md
├── examples/                         # 完整示例输出（虚构人物）
│   ├── 01-resume-rewrite.md          # 简历改写前后对比
│   ├── 02-jd-analysis.md             # JD 拆解报告
│   └── 03-interview-review.md        # 面试复盘报告
├── scripts/
│   ├── offer_calc.py
│   └── validate_skill.py
├── install.sh / install.ps1
├── CHANGELOG.md / CONTRIBUTING.md / LICENSE
├── .gitattributes / .gitignore
└── .github/workflows/validate.yml
```

## 设计原则

这三条是本技能与普通提示词集合的核心区别，也是所有输出必须遵守的底线：

**1. 绝不虚构用户数据。**
简历优化的边界是「重构表述」，不是「创造事实」。当你没提供量化数据时，它会输出
`【待确认：具体数值】` 并附上提问清单，而不是替你编一个看起来合理的数字 ——
编造的数据会在面试追问时直接崩盘。

**2. 薪资与行情数据必须现场检索。**
训练数据里的薪资数字会过期，直接背诵属于误导。所有薪资输出都标注来源、采集日期与样本范围，
并声明适用范围。无法联网时会明确告知，并给出检索关键词与信息渠道，而不是编造。

**3. 先给成品，再给说明。**
可直接复制使用的内容（改写后的简历、话术、文书全文）放在前面，方法论解释放在后面。

## 示例预览

`examples/` 下有 3 份完整示例，全部使用虚构人物。例如 `03-interview-review.md` 中的评分片段：

> **综合得分：6.8 / 10　→　评级：B**
>
> 你的**工程排错能力已经超过同层级候选人**（第 5 题 9 分），短板全部集中在
> 「表达选型依据」这一件事上 —— 这不是知识问题，而是准备方式问题。

## FAQ

**Q：支持社招吗？**
技能定位是校招 / 实习 / 初入职场。社招可复用的是简历改写、Offer 对比与谈判、职场沟通三部分；
面试模拟与 JD 拆解需要按社招场景调整提问深度。

**Q：薪资数据准确吗？**
不保证准确，只保证**有来源、有日期、有范围**。校招薪资受个人背景、面试表现、当年 HC 影响很大，
数据用于建立预期区间，不构成承诺。

**Q：可以在其他 AI 客户端用吗？**
`references/` 下的方法论文档是纯 Markdown，可独立阅读或移植。但要获得完整的技能触发与
工具调用能力，需要支持 Skill 机制的客户端。

**Q：示例里的人物是真的吗？**
全部虚构。示例中出现的「李思远」「星野科技」及所有数字均为演示用途。

## 贡献

欢迎补充题库、话术模板与行业数据。提交前请先运行：

```bash
python scripts/validate_skill.py .
python scripts/offer_calc.py --demo > /dev/null
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)
