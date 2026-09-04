# 常用命令配方

下面按任务组织命令，而不是要求你先掌握整套 SDK。先完成[安装](install.md)，激活运行环境；所有相对路径都以当前工作目录为起点。

## 检查 Skill 是否能调用运行时

```bash
hk --version
hk skill doctor --scope user --deep --json
```

如果使用项目级安装：

```bash
hk skill doctor --scope project --project-root . --deep --json
```

doctor 检查安装与运行环境，不评估模型对文档的理解能力。

## 不配模型，先跑一份合成演示

```bash
hk skill demo -o output/local-demo --json
```

回执提供 bundle、校验和工作台的输出位置。保留已有结果，换一个新目录运行下一次演示。

## 从文档开始

```bash
hk config init
hk list template
hk parse notes.md -t general/hypergraph -l zh --no-index -o output/notes-ka
hk bundle export output/notes-ka -o output/notes-bundle --json
```

抽取需要可用的模型配置。模板限定输出结构，但不保证实体、角色和事件范围自动正确。不要把密钥提交进仓库或放进公开命令截图。

## 从已有 bundle 开始

```bash
hk bundle validate output/notes-bundle --quality showcase --json
hk visualize output/notes-bundle -o output/notes-workbench.html --view contour --no-open --json
```

若希望初始打开关联视图，将 `--view contour` 改为 `--view incidence`。关联矩阵通过工作台内的独立按钮进入。

## 查看参数，不猜命令

```bash
hk parse --help
hk bundle export --help
hk bundle validate --help
hk visualize --help
hk skill --help
```

`--json` 用于获取支持该选项的命令回执；不是所有命令都有这个选项。界面操作、命令选项和原始数据字段也不是可以互换的名称。
