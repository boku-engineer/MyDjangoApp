# Git Workflow Instructions

When committing changes to this repository, always follow the PR workflow with a test-first approach.

## Naming Conventions

**Project names must be consistent with the local folder name.**
- Folder: `MyDjangoApp` → Project: `mydjangoapp`
- This ensures clarity and avoids confusion when working across multiple projects

## Workflow Steps

### 1. Create a Feature Branch

Before making any changes, create a new feature branch from main:

```bash
git checkout main
git pull origin main
git checkout -b feature/<feature-name>
```

### 2. Write Tests First

- Create or update test files in the appropriate test location
- Follow existing test patterns in the project
- Commit the tests separately:

```bash
git add <test_files>
git commit -m "Add tests for <feature>"
```

### 3. Implement the Feature

- Write the code to make the tests pass
- Run tests locally to verify:

```bash
python manage.py test
```

- Commit the implementation:

```bash
git add <feature_files>
git commit -m "Add <feature> implementation"
```

### 4. Push to Remote

```bash
git push -u origin feature/<feature-name>
```

### 5. Create a Pull Request

Use the GitHub CLI to create a PR:

```bash
gh pr create --title "<descriptive title>" --body "$(cat <<'EOF'
## Summary
- <bullet point describing change 1>
- <bullet point describing change 2>

## Test plan
- [ ] Tests pass locally
- [ ] Feature works as expected
- [ ] No regressions in existing functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### 6. Merge After Approval

After the PR is reviewed and approved:
- Merge via GitHub UI, or
- Use `gh pr merge` command

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Do NOT include Co-Authored-By tags for Claude Code

## Important Rules

1. **Never commit directly to main** - Always use feature branches and PRs
2. **Tests must pass** before creating a PR
3. **Write tests first** - This ensures testable code design
4. **One feature per PR** - Keep PRs focused and reviewable
5. **Project name = Folder name** - Keep naming consistent across the project
