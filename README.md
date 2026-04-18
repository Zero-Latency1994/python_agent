# python_agent

基于 **src 布局** 的 Python 项目骨架：业务代码放在 `src/`，测试放在 `tests/`，通用静态资源放在 `static/`。

## 目录结构

```
.
├── src/
│   └── my_app/          # 主应用包
├── tests/               # 单元测试
├── static/              # 静态资源或通用资源（如 Web 静态文件、模板附件等）
├── requirements.txt
├── pytest.ini
└── README.md
```

## 环境准备

建议使用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

## 运行测试

```powershell
pytest
```

`pytest.ini` 已将 `src` 加入 `pythonpath`，测试中可以 `import my_app`。

## 在代码中引用包

- 开发时：将 `src` 加入 `PYTHONPATH`，或使用上述 pytest 配置；若发布为可安装包，可后续增加 `pyproject.toml` 并 `pip install -e .`。
- 应用入口可放在 `src/my_app/` 下（例如 `main.py` 或 CLI 模块），按业务再拆分子包。

## 许可证

根据项目需要自行补充。
