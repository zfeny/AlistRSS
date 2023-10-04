## 介绍
一个针对个人用户、下载爱好者，实现无人RSS订阅下载并推送Alist的服务。

## 使用方法
- 修改data目录下的config.json文件
- 将需要订阅的rss源写入csv文件
  - url、path为必选值，其中path根据设置里用户的基本路径来设置
- 使用`chmod -x start.sh`给脚本赋予可执行权限
- `./start.sh`开启脚本，随后自动订阅RSS源并离线下载至Alist对应存储中。