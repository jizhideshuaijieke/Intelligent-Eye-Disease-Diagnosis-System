# 模型权重放置说明

默认情况下，根目录 `.gitignore` 不会上传 `*.pth` 权重文件，避免仓库过大和 GitHub 100MB 限制。

请将以下文件放到当前目录：

1. `best_model.pth`
2. `son_best_model.pth`
3. `seg_best_model.pth`
4. `oct_seg_best_model.pth`
5. `inceptionnext_tiny.pth`（如果你的模型代码依赖该文件）

如果你确实需要把权重也放到 GitHub，请使用 Git LFS：

```bash
git lfs install
git lfs track "模型/model_param/*.pth"
```
