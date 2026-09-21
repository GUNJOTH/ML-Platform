# 发布约定

本文档规定 `ML-Platform` 的版本、检查和 GitHub Release 流程。当前仓库没有自动
发布工作流，因此发布由仓库维护者按本约定手动完成。

## 版本与变更记录

- 本项目采用仓库级发布版本；版本来源分别是 `backend/pyproject.toml` 的
  `[project].version` 和 `frontend/package.json` 的 `version`。
- 当前两个版本字段均为 `0.1.0`。正式发布时，版本 PR 应同步更新两个字段，并使用
  `MAJOR.MINOR.PATCH` 版本格式和 `vMAJOR.MINOR.PATCH` Git tag。
- 用户可见的功能、修复、前后端契约、数据库迁移和配置变化必须先在
  `CHANGELOG.md` 的对应版本条目中记录。
- 版本号和更新日志在同一个 Pull Request 中修改；PR 目标为 `main`，不得直接推送
  或强推 `main`。
- 尚未形成正式版本的变化写入 `[未发布]`，不要在没有实际发布内容时伪造历史版本
  条目。

## 发布前检查

合并版本 PR 前，至少执行后端锁定依赖检查、Python 编译、前端锁定安装和生产构建：

```powershell
Push-Location backend
uv lock --check
python -m compileall -q app
Pop-Location

Push-Location frontend
pnpm install --frozen-lockfile
pnpm run build
Pop-Location
```

如果本次发布包含部署包，还要在受控环境执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\package-deploy.ps1
```

并确认生成的 `ai-platform-deploy-YYYYMMDD.zip` 不包含 `.env`、运行期存储、依赖
缓存、前端开发产物或其他敏感文件。涉及数据库迁移时，还要在隔离数据库验证
`alembic upgrade head` 和服务健康检查；本地编译不能替代数据库验证。

如果默认分支的 CI 尚未覆盖本次变更，必须在 PR 中附上上述命令的实际输出；CI 合并
到默认分支后，以对应后端和前端工作流结果作为持续验证证据。

## 发布步骤

1. 从 `main` 创建版本 PR，同步更新后端和前端版本号，并更新 `CHANGELOG.md`。
2. 等待后端锁定检查、Python 编译和前端构建通过，完成代码、数据库迁移、部署包和
   敏感信息审查后合并。
3. 在已合并的 `main` 提交上创建对应的 `vMAJOR.MINOR.PATCH` tag，并推送该 tag；
   不修改或覆盖已有 tag。
4. 基于该 tag 创建 GitHub Release，标题使用版本号，正文引用
   `CHANGELOG.md` 中对应版本条目，并注明数据库迁移、配置变化、部署包和已知限制。
5. 发布后确认 Release、tag 和两个版本字段一致；如发现问题，按补丁版本发布修复，
   不回写已发布版本。

## 回滚边界

发布回滚不得通过删除或覆盖 tag 伪造历史。前端静态资源、后端服务、数据库迁移和
部署配置的回滚必须分别评估；如果迁移不可逆，应保留原版本证据，并通过前向修复或
明确的迁移说明处理。
