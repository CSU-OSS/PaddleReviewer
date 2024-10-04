# CMG-server

## Run
先切换到manage.py的同名文件夹下，运行命令
`python manage.py runserver`

## 接口文档

- 本地部署接口地址：http://127.0.0.1:8000

- 服务器部署地址：http://47.119.169.38:8000

支持接口：
接口名称						|请求方式 | 结果 | 描述 |
:---- |:--- |:---- |:---
/cmg | GET/POST | commit message | 根据指定diff生成commit message


### 1. /cmg

#### 1.1 参数
参数名称 | 参数类型 | 描述 | 参数要求
:---- |:--- |:---- |:---
diff | str | 代码变更字符串 | 必选
historyMessage | List[str] | 历史提交消息列表 | 可选
needRec | bool | 是否推荐5条 | 可选
temperature | float | 温度，用于控制模型的输出的随机性。默认0.9 | 可选
max_tokens | int | 最大输出token数量 | 可选

#### 1.2 请求示例

```
# GET 方式
http://47.119.169.38:8000/cmg?diff=def hello()&needRec=true&historyMessage=["Added a"]

# POST 方式
http://47.119.169.38:8000/cmg

{
    "diff": "def hello()",
    "historyMessage": ["Added"],
    "needRec": 1
}

```

#### 1.3 响应结果

```
{
    "commit_message": "Added a hello function."
}
or
{
    "commit_message": [
        "Add missing file",
        "Fixes #1234",
        "Add new feature",
        "Update readme",
        "Improve user experience"
    ]
}
```

## 3 附录A 响应码说明

响应码	|说明  
:----	|:---
200		|处理成功
301		|解析报文错误
302		|无效调用凭证
303		|参数不正确
500		|系统内部错误
999		|处理失败


