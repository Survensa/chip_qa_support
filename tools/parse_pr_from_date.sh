#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 --dir <directory> --from <since_date> [--to <until_date>]"
  echo "  --dir      [PWD path] Directory to check"
  echo "  --from     [YYYY-MM-DD] The date to check from"
  echo "  --to       [YYYY-MM-DD] The date to check to (default: latest)"
  exit 1
}

# Parse command-line arguments
TO_DATE="HEAD"  # Default to latest commit if --to is not provided

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --dir) DIRECTORY="$2"; shift ;;
    --from) SINCE_DATE="$2"; shift ;;
    --to) TO_DATE="$2"; shift ;;
    *) usage ;;
  esac
  shift
done

# Check if both required arguments are provided
if [[ -z "$DIRECTORY" || -z "$SINCE_DATE" ]]; then
  usage
fi

# Validate inputs
if [[ ! -d "$DIRECTORY" ]]; then
  echo "Error: Directory '$DIRECTORY' does not exist."
  exit 1
fi

# Change to the specified directory
cd "$DIRECTORY" || { echo "Error: Could not change to directory '$DIRECTORY'"; exit 1; }

# Check if we're in the correct directory
echo "Current directory: $(pwd)"

# Find commits between the specified dates affecting files in the directory
echo "Running git log command for files in the directory..."

git log --since="$SINCE_DATE" --until="$TO_DATE" --pretty=format:"%H %ad %s" --name-only --date=format:'%Y-%m-%d' -- "$DIRECTORY" | awk '
  /^[0-9a-f]{40} / {
    commit_hash = $1
    commit_date = $2
    pr_number = ""
    for (i = 3; i <= NF; i++) {
      if ($i ~ /#([0-9]+)/) {
        pr_number = substr($i, 2, length($i) - 2)
        pr_number = gensub(/\)$/, "", "g", pr_number)
        break
      }
    }
  }
  /^[^0-9a-f]/ {
    if (pr_number != "") {
      file_path = $1
      file_name = gensub(/.*\//, "", "g", file_path)
      printf "%-12s | %-30s | %-5s\n", commit_date, file_name, pr_number
    }
  }
' | sort -u

# Check the exit status of the previous command
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to run git log command."
fi
