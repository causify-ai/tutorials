#!/usr/bin/env bash
#
# check_pr.sh
#  1) Moves to the Git repository root
#  2) Checks for any binary files staged for commit
#  3) Lists the top N largest added/modified/copied files between upstream and your branch

# ─── 1. Jump to repo root ──────────────────────────────────────────
cd "$(git rev-parse --show-toplevel)" || exit 1

# ─── 2. Parse arguments ───────────────────────────────────────────
UPSTREAM="origin/master"
BRANCH=""
TOP=10

while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--upstream)
      UPSTREAM="$2"; shift 2;;
    -b|--branch)
      BRANCH="$2"; shift 2;;
    -n|--top)
      TOP="$2"; shift 2;;
    *)
      echo "Unknown argument: $1"; exit 1;;
  esac
done

# Default to current branch if none provided
if [[ -z "$BRANCH" ]]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

echo "Inspecting changes on '${BRANCH}' vs '${UPSTREAM}'"

# ─── 3. Check for staged binary files ────────────────────────────
if git diff --cached --numstat | grep -qE '^\-\s*\-'; then
  echo "⛔ Binary files detected in staging. Please remove them before committing."
  exit 1
else
  echo "✅ No binary files in staging."
fi

# ─── 4. List top N largest files in the diff ─────────────────────
echo -e "\n🔍 Top ${TOP} largest files in ${UPSTREAM}...${BRANCH}:"
git diff --diff-filter=ACM --name-only "${UPSTREAM}...${BRANCH}" \
  | xargs du -k 2>/dev/null \
  | sort -rn \
  | head -n "${TOP}" \
  | awk '{ printf("%.2fM\t%s\n", $1/1024, $2) }'
