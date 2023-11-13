# FRPC守护进程
这是一个FRPC自动配置守护程序，定时从服务器获取最新的配置文件并管理FRPC进程。

这个程序设计上和MUA Union API、MUA联合大厅一同使用，以便MUA服务器网络能够添加更多的入口节点。

## 安装
- 下载或`git clone`，解压
- 安装依赖：运行`pip install -r requirements.txt`
- 将`frpc`(Linux)或`frpc.exe`(Windows)放到`frpc`目录下
- linux可能需要赋予frpc执行权限：`chmod +x frpc/frpc`
- 按需修改`config.py`
- 启动命令：`python3 daemon.py`

## 配置文件
配置文件位于`config.py`，请参考注释进行修改。

其中`Union Member Key`填写皮肤站 插件配置 > Yggdrasil API 配置 > Union API配置 > Union Member Key 处获取到的值。

如果你没有部署皮肤站，请联系开发者或者管理员获取一个Key。

## 扩展
扩展位于`extensions`目录下。删除文件名开头的`#`以启用该扩展。

考虑到没有需求，因此没有扩展文档。

### Velocity/Bungeecord
如果你使用二级代理接入MUA服务器网络，可以考虑启用minecraft扩展。
- 拷贝Velocity的文件到`server`文件夹
- 去掉文件名开头的`#`
- 修改`minecraft.py`，修改`START_COMMAND`为你的启动指令

#### 自动更新
##### FRPC本体
启用`autoupdate_frpc.py`和`download_github_release.py`。
**需要能访问GitHub**

##### Velocity/Bungeecord
启用`autoupdate_velocity.py`或`autoupdate_bungeecord.py`，修改其中的jar文件名。

##### 插件
启用`autoupdate_plugins.py`。对于spigotmc上的插件，你需要知道resource id。
- 如ViaVersion的链接为`https://www.spigotmc.org/resources/viaversion.19254/`，其resource id为19254。
- 添加到`SPIGET_PLUGINS`，形如`(<resource id>, <jar名称>)`

对于GitHub上的插件，你需要提供repo的路径。**需要能访问GitHub**。
- 添加到`GITHUB_PLUGINS`，形如`(<repo>, <jar名称>, [可选，release file的正则表达式])`

## 从旧版升级
旧版扩展中`velocity.py`被更名成`minecraft.py`，并修改了默认值。修改了一部分`config.py`中的值。
建议操作步骤：
- 备份旧文件。至少备份`velocity.py`、`config.py`和你的Minecraft目录。
- 下载源码，复制Minecraft目录，根据以前的`velocity.py`和`config.py`修改新版的`minecraft.py`和`config.py`。