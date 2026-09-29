#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_skill.py — SKILL.md 格式校验器（自包含，无第三方依赖）

本脚本刻意不依赖 WorkBuddy 内置的 skill-creator 脚本，便于在 GitHub Actions
等任意环境中运行，也方便贡献者在本地提交前自检。

用法
----
    python scripts/validate_skill.py            # 校验仓库根目录（默认）
    python scripts/validate_skill.py <skill-dir>

校验项
------
  1. SKILL.md 存在于技能根目录
  2. YAML frontmatter 由 --- 正确包裹，且可解析
  3. 必填字段：name / description / agent_created
  4. name 与目录名一致，且符合 ^[a-z0-9][a-z0-9-]*$
  5. description 长度合理（>= 50 字符）且不跨行
  6. SKILL.md 中以反引号引用的 references/ scripts/ assets/ examples/ 路径真实存在
  7. 无遗留的 TODO / FIXME 占位符

退出码：0 = 通过，1 = 存在错误
"""

import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REQUIRED_FIELDS = ("name", "description", "agent_created")
REF_PATTERN = re.compile(
    r"`((?:references|scripts|assets|examples)/[A-Za-z0-9._\-/]+)`"
)
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")
DESC_MIN_LEN = 50


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)


def parse_frontmatter(text, report):
    """返回 frontmatter 的键值字典；解析失败返回 None。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report.error("SKILL.md 未以 `---` 开头，缺少 YAML frontmatter")
        return None

    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        report.error("frontmatter 未闭合，缺少结尾的 `---`")
        return None

    fields = {}
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            report.warn("frontmatter 中无法解析的行：%r" % raw)
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def validate(skill_dir):
    report = Report()
    skill_dir = os.path.abspath(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.isfile(skill_md):
        report.error("未找到 SKILL.md：%s" % skill_md)
        return report

    with open(skill_md, "r", encoding="utf-8") as fh:
        text = fh.read()

    fields = parse_frontmatter(text, report)
    if fields is None:
        return report

    # --- 必填字段
    for key in REQUIRED_FIELDS:
        if key not in fields or not fields[key]:
            report.error("frontmatter 缺少必填字段：%s" % key)

    # --- agent_created
    if fields.get("agent_created", "").lower() not in ("true", "yes", "1"):
        report.warn(
            "agent_created 未设置为 true，后续可能无法通过 skill_manage 修改该技能"
        )

    # --- name
    name = fields.get("name", "")
    if name:
        if not NAME_RE.match(name):
            report.error(
                "name %r 不符合命名规范，只允许小写字母、数字与连字符，且需以字母或数字开头" % name
            )
        dir_name = os.path.basename(skill_dir.rstrip("/\\"))
        if dir_name != name:
            report.error(
                "name (%s) 与目录名 (%s) 不一致，安装后可能导致技能无法正确加载"
                % (name, dir_name)
            )

    # --- description
    desc = fields.get("description", "")
    if desc:
        if len(desc) < DESC_MIN_LEN:
            report.error(
                "description 过短（%d 字符，建议 >= %d），无法让模型判断触发时机"
                % (len(desc), DESC_MIN_LEN)
            )
        if ": " in desc:
            report.warn(
                "description 含半角冒号加空格，可能破坏 YAML 解析；建议改用全角「：」"
            )

    # --- 引用路径存在性
    refs = sorted(set(REF_PATTERN.findall(text)))
    missing = [r for r in refs if not os.path.exists(os.path.join(skill_dir, r))]
    for path in missing:
        report.error("SKILL.md 中引用了不存在的路径：%s" % path)

    # --- 占位符
    for lineno, line in enumerate(text.splitlines(), 1):
        match = PLACEHOLDER_RE.search(line)
        if match:
            report.warn("第 %d 行存在未完成的占位符：%s" % (lineno, match.group(0)))

    # --- 结构提示
    for directory in ("references", "scripts", "assets", "examples"):
        path = os.path.join(skill_dir, directory)
        if os.path.isdir(path) and not os.listdir(path):
            report.warn("目录 %s/ 存在但为空，建议删除或补充内容" % directory)

    report.refs_checked = len(refs)
    return report


def main(argv):
    target = argv[1] if len(argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    report = validate(target)

    print("校验目标：%s" % os.path.abspath(target))
    print("引用路径检查：%d 个" % getattr(report, "refs_checked", 0))

    for message in report.warnings:
        print("  [warn]  %s" % message)
    for message in report.errors:
        print("  [error] %s" % message)

    if report.errors:
        print("\nSkill is INVALID! 共 %d 个错误，%d 个警告。" % (len(report.errors), len(report.warnings)))
        return 1

    print("\nSkill is valid!  %d 个警告。" % len(report.warnings))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
