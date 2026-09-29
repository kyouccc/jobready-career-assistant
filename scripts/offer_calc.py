#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""offer_calc.py — Offer 总包换算计算器

把「只比月薪」升级为「比年度现金 + 公积金 + 实际时薪」。

纯标准库实现，无第三方依赖，Python 3.8+。

用法
----
    python offer_calc.py --demo
    python offer_calc.py offers.json
    python offer_calc.py offers.json --format markdown
    python offer_calc.py offers.json --json-out result.json

输入格式（JSON）
---------------
{
  "assumptions": {                     // 可选：全局默认值，可被单个 offer 覆盖
    "work_weeks_per_year": 50,
    "social_insurance_rate": 0.105,
    "tax_rate": 0.10
  },
  "offers": [
    {
      "name": "A 公司 · 算法工程师",
      "monthly_salary": 22000,          // 必填：税前月薪
      "months": 12,                     // 薪资发放月数，默认 12
      "year_end_months": 3,             // 年终奖月数，默认 0
      "year_end_guaranteed": false,     // 是否写入合同，默认 false
      "allowances_monthly": 1500,       // 月度补贴（餐补/房补/交通），默认 0
      "signing_bonus": 30000,           // 签字费（一次性），默认 0
      "equity_annual": 0,               // 股票/RSU 年均价值，默认 0（单独列示）
      "housing_fund_rate": 0.12,        // 公积金缴存比例（单边），默认 0.12
      "housing_fund_base": 22000,       // 公积金缴存基数，默认 = monthly_salary
      "social_insurance_rate": 0.105,   // 社保个人缴纳比例，默认 0.105
      "tax_rate": 0.10,                 // 个税实际税负率（估算），默认 0.10
      "work_hours_per_week": 45,        // 含加班的实际周工时，默认 40
      "rent_monthly": 3500,             // 房租，默认 0
      "commute_monthly": 300,           // 通勤，默认 0
      "living_monthly": 2500,           // 其他生活支出，默认 0
      "probation_months": 3,            // 试用期时长，默认 0
      "probation_salary_ratio": 0.8,    // 试用期工资比例，默认 1.0
      "notes": "年终奖为口头承诺"        // 备注，默认空
    }
  ]
}

计算口径
--------
年度现金总额（保证部分）= 月薪 × 发放月数 + 月度补贴 × 12 + 签字费
                          + （年终奖月数 × 月薪，仅当 year_end_guaranteed 为 true）
年度现金总额（浮动部分）= 年终奖月数 × 月薪，仅当未写入合同时单独列示
公积金年收益（双边）    = 缴存基数 × 缴存比例 × 2 × 12
月度到手现金            = 月薪 − 社保个人缴纳 − 公积金个人缴纳 − 个税
月度可支配余额          = 月度到手现金 − 房租 − 通勤 − 生活支出
月度综合收益            = 月度到手现金 + 公积金双边月缴 − 房租 − 通勤 − 生活支出
实际时薪                = 年度现金总额 ÷ （周工时 × 年工作周数）
首年试用期折损          = 试用期月数 × 月薪 ×（1 − 试用期工资比例）

注意：社保/个税采用比例估算，非逐级累进精算；结果用于横向比较，不等同于实际到手金额。
"""

import argparse
import json
import sys

# ---------------------------------------------------------------- 默认假设

DEFAULTS = {
    "work_weeks_per_year": 50,
    "social_insurance_rate": 0.105,
    "tax_rate": 0.10,
    "housing_fund_rate": 0.12,
    "months": 12,
    "work_hours_per_week": 40,
    "probation_salary_ratio": 1.0,
}

DEMO_INPUT = {
    "assumptions": {"work_weeks_per_year": 50},
    "offers": [
        {
            "name": "A 公司 · 算法工程师",
            "monthly_salary": 22000,
            "months": 12,
            "year_end_months": 3,
            "year_end_guaranteed": False,
            "allowances_monthly": 1500,
            "signing_bonus": 30000,
            "housing_fund_rate": 0.12,
            "housing_fund_base": 22000,
            "work_hours_per_week": 45,
            "rent_monthly": 3500,
            "commute_monthly": 300,
            "living_monthly": 2500,
            "probation_months": 3,
            "probation_salary_ratio": 0.8,
            "notes": "年终奖为口头承诺，未写入合同",
        },
        {
            "name": "B 公司 · 算法工程师",
            "monthly_salary": 20000,
            "months": 14,
            "year_end_months": 2,
            "year_end_guaranteed": True,
            "allowances_monthly": 800,
            "signing_bonus": 10000,
            "housing_fund_rate": 0.05,
            "housing_fund_base": 8000,
            "work_hours_per_week": 55,
            "rent_monthly": 3200,
            "commute_monthly": 400,
            "living_monthly": 2500,
            "probation_months": 6,
            "probation_salary_ratio": 0.8,
            "notes": "公积金按最低基数缴纳；大小周",
        },
    ],
}

# ---------------------------------------------------------------- 计算逻辑

METRIC_LABELS = [
    ("annual_cash_guaranteed", "年度现金（保证部分）"),
    ("annual_cash_floating", "年度现金（浮动部分）"),
    ("annual_cash_total", "年度现金总额"),
    ("equity_annual", "股票/期权年均价值"),
    ("annual_total_package", "年度总包（含股票）"),
    ("housing_fund_annual", "公积金年收益（双边）"),
    ("monthly_net_cash", "月度到手现金"),
    ("monthly_disposable", "月度可支配余额"),
    ("monthly_total_benefit", "月度综合收益（含公积金）"),
    ("annual_hours", "年工作小时数"),
    ("effective_hourly", "实际时薪"),
    ("first_year_probation_loss", "首年试用期折损"),
]

CURRENCY_KEYS = {
    "annual_cash_guaranteed",
    "annual_cash_floating",
    "annual_cash_total",
    "equity_annual",
    "annual_total_package",
    "housing_fund_annual",
    "monthly_net_cash",
    "monthly_disposable",
    "monthly_total_benefit",
    "effective_hourly",
    "first_year_probation_loss",
}

INT_KEYS = {"annual_hours"}


def _num(offer, key, default=0.0):
    """读取数值字段，缺失或非法时返回 default。"""
    value = offer.get(key, None)
    if value is None:
        return float(default)
    if isinstance(value, bool):
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _merged(offer, assumptions, key):
    """按 offer → assumptions → DEFAULTS 的优先级取值。"""
    if key in offer and offer[key] is not None:
        return offer[key]
    if key in assumptions and assumptions[key] is not None:
        return assumptions[key]
    return DEFAULTS.get(key)


def compute(offer, assumptions):
    """计算单个 offer 的全部指标，返回 (metrics dict, warnings list)。"""
    warnings = []

    monthly = _num(offer, "monthly_salary", 0.0)
    if monthly <= 0:
        raise ValueError("offer %r 缺少必填字段 monthly_salary（税前月薪）" % offer.get("name", "?"))

    months = _num(offer, "months", _merged(offer, assumptions, "months"))
    year_end_months = _num(offer, "year_end_months", 0.0)
    year_end_guaranteed = bool(offer.get("year_end_guaranteed", False))
    allowances = _num(offer, "allowances_monthly", 0.0)
    signing = _num(offer, "signing_bonus", 0.0)
    equity = _num(offer, "equity_annual", 0.0)

    hf_rate = _num(offer, "housing_fund_rate", _merged(offer, assumptions, "housing_fund_rate"))
    hf_base = offer.get("housing_fund_base", None)
    hf_base = float(hf_base) if hf_base not in (None, "") else monthly
    social_rate = _num(
        offer, "social_insurance_rate", _merged(offer, assumptions, "social_insurance_rate")
    )
    tax_rate = _num(offer, "tax_rate", _merged(offer, assumptions, "tax_rate"))

    hours_per_week = _num(
        offer, "work_hours_per_week", _merged(offer, assumptions, "work_hours_per_week")
    )
    weeks = _num(
        offer, "work_weeks_per_year", _merged(offer, assumptions, "work_weeks_per_year")
    )

    rent = _num(offer, "rent_monthly", 0.0)
    commute = _num(offer, "commute_monthly", 0.0)
    living = _num(offer, "living_monthly", 0.0)

    probation_months = _num(offer, "probation_months", 0.0)
    probation_ratio = _num(
        offer, "probation_salary_ratio", _merged(offer, assumptions, "probation_salary_ratio")
    )

    # --- 年度现金
    year_end_total = year_end_months * monthly
    base_cash = monthly * months + allowances * 12 + signing
    if year_end_guaranteed:
        annual_guaranteed = base_cash + year_end_total
        annual_floating = 0.0
    else:
        annual_guaranteed = base_cash
        annual_floating = year_end_total
        if year_end_total > 0:
            warnings.append("年终奖未写入合同，已计入浮动部分")
    annual_cash_total = annual_guaranteed + annual_floating
    annual_total_package = annual_cash_total + equity

    # --- 公积金
    housing_fund_annual = hf_base * hf_rate * 2 * 12

    # --- 月度
    social_personal = monthly * social_rate
    hf_personal = hf_base * hf_rate
    tax = monthly * tax_rate
    monthly_net_cash = monthly - social_personal - hf_personal - tax
    monthly_disposable = monthly_net_cash - rent - commute - living
    monthly_total_benefit = monthly_net_cash + hf_base * hf_rate * 2 - rent - commute - living

    # --- 时薪
    annual_hours = hours_per_week * weeks
    effective_hourly = annual_cash_total / annual_hours if annual_hours else 0.0

    # --- 试用期
    first_year_probation_loss = probation_months * monthly * (1 - probation_ratio)

    # --- 数据完整性提醒
    if monthly_disposable < 0:
        warnings.append("月度可支配为负：请核对生活成本字段是否填写完整")
    if hf_base != monthly:
        warnings.append("公积金基数(%.0f)与月薪(%.0f)不一致" % (hf_base, monthly))
    if hours_per_week > 44:
        warnings.append("周工时 %.0f 小时高于法定标准工时" % hours_per_week)

    metrics = {
        "annual_cash_guaranteed": annual_guaranteed,
        "annual_cash_floating": annual_floating,
        "annual_cash_total": annual_cash_total,
        "equity_annual": equity,
        "annual_total_package": annual_total_package,
        "housing_fund_annual": housing_fund_annual,
        "monthly_net_cash": monthly_net_cash,
        "monthly_disposable": monthly_disposable,
        "monthly_total_benefit": monthly_total_benefit,
        "annual_hours": annual_hours,
        "effective_hourly": effective_hourly,
        "first_year_probation_loss": first_year_probation_loss,
    }
    return metrics, warnings


# ---------------------------------------------------------------- 输出渲染


def _fmt(key, value):
    if key in INT_KEYS:
        return "{:,.0f}".format(value)
    if key in CURRENCY_KEYS:
        if key == "effective_hourly":
            return "¥{:,.1f}/h".format(value)
        return "¥{:,.0f}".format(value)
    return "{:,.2f}".format(value)


def _pad(text, width):
    """按显示宽度补齐（中文按 2 列计）。"""
    display = 0
    for ch in text:
        display += 2 if ord(ch) > 0x2E80 else 1
    return text + " " * max(0, width - display)


def render_text(results, warnings_map, assumptions):
    names = [r["name"] for r in results]
    col_widths = [max(20, len(n) * 2 + 2) for n in names]
    label_width = 26

    lines = []
    lines.append("=" * (label_width + sum(col_widths) + 2))
    lines.append("Offer 总包对比（估算值，用于横向比较，不等同实际到手）")
    lines.append("=" * (label_width + sum(col_widths) + 2))

    header = _pad("指标", label_width)
    for name, width in zip(names, col_widths):
        header += _pad(name, width)
    lines.append(header)
    lines.append("-" * (label_width + sum(col_widths) + 2))

    for key, label in METRIC_LABELS:
        row = _pad(label, label_width)
        for r, width in zip(results, col_widths):
            row += _pad(_fmt(key, r["metrics"][key]), width)
        lines.append(row)

    lines.append("-" * (label_width + sum(col_widths) + 2))

    for r in results:
        notes = r.get("notes", "")
        warn = warnings_map.get(r["name"], [])
        detail = "; ".join(warn + ([notes] if notes else []))
        if detail:
            lines.append("· {}: {}".format(r["name"], detail))

    lines.append("")
    lines.append(
        "口径假设：年工作周数 {:.0f} 周；社保个人缴纳 {:.1%}；个税税负率 {:.1%}；"
        "公积金默认比例 {:.0%}".format(
            _num({}, "x", _merged({}, assumptions, "work_weeks_per_year")),
            _num({}, "x", _merged({}, assumptions, "social_insurance_rate")),
            _num({}, "x", _merged({}, assumptions, "tax_rate")),
            _num({}, "x", _merged({}, assumptions, "housing_fund_rate")),
        )
    )
    lines.append("社保与个税按比例估算，非逐级累进精算。数据仅供参考，不构成承诺。")
    return "\n".join(lines)


def render_markdown(results, warnings_map, assumptions):
    names = [r["name"] for r in results]
    lines = []
    lines.append("| 指标 | " + " | ".join(names) + " |")
    lines.append("|---" * (len(names) + 1) + "|")
    for key, label in METRIC_LABELS:
        cells = [_fmt(key, r["metrics"][key]) for r in results]
        lines.append("| **{}** | ".format(label) + " | ".join(cells) + " |")

    lines.append("")
    lines.append("**风险与备注**")
    lines.append("")
    for r in results:
        warn = warnings_map.get(r["name"], [])
        notes = r.get("notes", "")
        detail = "；".join(warn + ([notes] if notes else []))
        lines.append("- **{}**：{}".format(r["name"], detail or "无"))

    lines.append("")
    lines.append(
        "> 口径假设：年工作周数 {:.0f} 周；社保个人缴纳 {:.1%}；个税税负率 {:.1%}。"
        "社保与个税按比例估算，非逐级累进精算。数据仅供参考，不构成承诺。".format(
            _num({}, "x", _merged({}, assumptions, "work_weeks_per_year")),
            _num({}, "x", _merged({}, assumptions, "social_insurance_rate")),
            _num({}, "x", _merged({}, assumptions, "tax_rate")),
        )
    )
    return "\n".join(lines)


# ---------------------------------------------------------------- 入口


def run(payload):
    assumptions = payload.get("assumptions", {}) or {}
    offers = payload.get("offers", [])
    if not offers:
        raise ValueError("输入中缺少 offers 数组，或数组为空")

    results = []
    warnings_map = {}
    for offer in offers:
        metrics, warnings = compute(offer, assumptions)
        name = offer.get("name") or ("Offer %d" % (len(results) + 1))
        results.append(
            {"name": name, "metrics": metrics, "notes": offer.get("notes", "")}
        )
        warnings_map[name] = warnings
    return results, warnings_map, assumptions


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offer 总包换算计算器：比年度现金、公积金与实际时薪，而不只是月薪。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", nargs="?", help="输入 JSON 文件路径")
    parser.add_argument(
        "--demo", action="store_true", help="使用内置示例数据运行，并打印示例输入"
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="输出格式，默认 text",
    )
    parser.add_argument("--json-out", metavar="PATH", help="将计算结果另存为 JSON")
    args = parser.parse_args(argv)

    if args.demo:
        payload = DEMO_INPUT
        print("--- 示例输入（JSON） ---")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print()
    else:
        if not args.input:
            parser.error("请提供输入 JSON 文件路径，或使用 --demo 查看示例")
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

    results, warnings_map, assumptions = run(payload)

    if args.format == "markdown":
        print(render_markdown(results, warnings_map, assumptions))
    else:
        print(render_text(results, warnings_map, assumptions))

    if args.json_out:
        out = {
            "assumptions": assumptions,
            "results": [
                {"name": r["name"], "notes": r.get("notes", ""), **r["metrics"]}
                for r in results
            ],
            "warnings": warnings_map,
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print("\n结果已写入 {}".format(args.json_out))

    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        sys.exit(main())
    except (ValueError, json.JSONDecodeError) as exc:
        print("输入有误：{}".format(exc), file=sys.stderr)
        sys.exit(1)
