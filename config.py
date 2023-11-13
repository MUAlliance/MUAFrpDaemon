import schedule

# frpc二进制文件名
#FRPC_BIN = "frpc"
# frpc所在目录
FRPC_DIR = "frpc"
# 更新定时器，设置请参考schedule包
FRPC_SYNC_SCHEDULE = schedule.every().hour
# API地址
FRPC_UNION_API_NETWORK = "https://skin.mualliance.ltd/api/union/network"
# Union Member Key
FRPC_UNION_MEMBER_KEY = ""
# 填写在frpc config中需要替换的部分，字典的键是要替换占位符
# 目前只需替换metas和servers
FRPC_CONFIG_PLACEHOLDERS = {
    "metas" : '''
metadatas.domain = 
metadatas.domain_alias = 
metadatas.forced_hosts = 
    ''',
    "servers" : '''
[[proxies]]
name = "SJMC"
type = "tcp"
localIp = "127.0.0.1"
localPort = 00000
remotePort = 00000
    '''
}

# 是否开启调试输出
DEBUG_ENABLED = False