#!/usr/bin/env bash
# 把本仓库安装为 WorkBuddy 用户级技能。
#
# 用法：
#   bash install.sh                  # 安装到 ~/.workbuddy-ai/skills/
#   bash install.sh --force          # 已存在时直接覆盖，不再询问
#   bash install.sh --yes            # 自动确认
#   bash install.sh --dir /path/to/skills   # 自定义技能根目录
#
# 也可用环境变量指定技能根目录：
#   WORKBUDDY_SKILLS_DIR=/path/to/skills bash install.sh

set -euo pipefail

SKILL_NAME="jobready-career-assistant"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${WORKBUDDY_SKILLS_DIR:-$HOME/.workbuddy-ai/skills}"
ITEMS=(SKILL.md references assets scripts examples)

FORCE=0
ASSUME_YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    --dir)
      if [ $# -lt 2 ]; then echo "错误：--dir 需要提供路径" >&2; exit 1; fi
      DEST_ROOT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "错误：未知参数 $1" >&2; exit 1 ;;
  esac
done

DEST_DIR="$DEST_ROOT/$SKILL_NAME"

echo "源目录：  $SRC_DIR"
echo "目标目录：$DEST_DIR"
echo

# --- 校验源目录确实是一个技能
if [ ! -f "$SRC_DIR/SKILL.md" ]; then
  echo "错误：源目录下未找到 SKILL.md，请确认在仓库根目录执行本脚本。" >&2
  exit 1
fi

# --- 已存在时的处理
if [ -e "$DEST_DIR" ]; then
  if [ "$FORCE" -eq 0 ]; then
    if [ "$ASSUME_YES" -eq 0 ]; then
      printf '目标目录已存在，是否覆盖？[y/N] '
      read -r reply || reply=""
      case "$reply" in
        [yY]|[yY][eE][sS]) ;;
        *) echo "已取消，未做任何修改。"; exit 0 ;;
      esac
    fi
  fi
  echo "正在移除旧版本……"
  rm -rf "$DEST_DIR"
fi

mkdir -p "$DEST_DIR"

# --- 只复制技能运行所需内容，不复制仓库管理文件
for item in "${ITEMS[@]}"; do
  if [ -e "$SRC_DIR/$item" ]; then
    cp -r "$SRC_DIR/$item" "$DEST_DIR/"
    echo "  已安装 $item"
  else
    echo "  跳过（不存在）$item"
  fi
done

echo
echo "安装完成：$DEST_DIR"

# --- 可选：顺手跑一次校验
if command -v python >/dev/null 2>&1; then
  echo
  python "$DEST_DIR/scripts/validate_skill.py" "$DEST_DIR" || true
elif command -v python3 >/dev/null 2>&1; then
  echo
  python3 "$DEST_DIR/scripts/validate_skill.py" "$DEST_DIR" || true
fi

echo
echo "若技能未立即生效，请重启 WorkBuddy 客户端。"
