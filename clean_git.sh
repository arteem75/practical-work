# Remove tracked files of these types
find . -name __pycache__ -print0 | xargs -0 git rm -rf --ignore-unmatch
find . -name "*.pyc" -print0 | xargs -0 git rm -f --ignore-unmatch
find . -name .DS_Store -print0 | xargs -0 git rm -f --ignore-unmatch
git rm -rf .vscode/ 2>/dev/null || true

# Clean from filesystem too
find . -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name .DS_Store -delete
rm -rf .vscode/ 2>/dev/null || true