find . -type f -name '*.py' \
  | sort \
  | while read file; do
      echo "$file"
      grep -E '^\s*(class|def) ' "$file" \
        | sed -E 's/^(\s*)(class|def) +([[:alnum:]_]+)/\1└── \2 \3()/'
    done
