# PaddleReviewer
基于飞桨的代码评审插件

该仓库包含我们项目的所有代码。提交代码时请严格按照目录规范，不要多提交不必要的文件，如'__pycache__'这种，请在.gitignore里面过滤掉。开发完一个功能，自测OK后提交代码，保证每一个commit是较简短且清晰的，能从commit message里了解代码变更内容。

## 目录结构规范

NAME
├── README.md 介绍项目文档入口
└── PaddleReviewer-JetBrains JetBrains端的前端代码
    ├── docs          文档
    ├── src           核心源码
        ├── XXX     具体模块
        ├── ...       ...
└── PaddleReviewer-Backend 后端代码
    ├── docs          文档
    ├── src           核心源码
        ├── XXX     具体模块
        ├── ...       ...

