---
name: package
description: 发布或整理 DeepScholar-Agent 仓库前清理文件、检查公开内容和提交范围。Use when user asks 打包、发布、push、提交 GitHub、清理仓库、before release.
---

# DeepScholar-Agent Package Skill

## 发布前检查

1. 不提交 `.env`、`.venv`、缓存、真实论文、个人隐私文件。
2. 保留 `examples/demo_run/` 和 `workspace/` 中可展示样例。
3. `git status --short --branch` 查看是否有非本次改动。
4. `git diff --check` 检查空白错误。
5. 如代码变化，运行 unittest / smoke check。
6. README 和 docs 必须与真实代码能力一致。

## Git 命令

```powershell
git add <target-files>
git commit -m "<clear message>"
git push origin main
```
