from .main import *

__zx_plugin_name__ = "音游开字符"
__plugin_usage__ = """
usage:
    开字符 ?[题数]
    (题数默认10)
    打开/k [字符]
    (长度不限,数量不限)
    验证 [歌名] [编号]
    (不区分大小写)
    结束
    (不玩了跑路({题目数量}min内仅限发起人可操作,{题目数量}min后所有成员均可))
    c[编号].[歌名]
    (一种简便猜歌的方法)
    
    曲库不足，欢迎提供

    指令：
        开字符 20
        打开 ä 
        k a e i o u
        验证 rrhar'il 3
        c2.igallta
        结束
""".strip()
__plugin_des__ = "音游开字符"
__plugin_cmd__ = ["k/打开","开字符","验证/c","结束"]
__plugin_settings__ = {
    "cmd": __plugin_cmd__,
}
__plugin_type__ = ("群内小游戏",1)
__plugin_version__ = 0.1
__plugin_author__ = "SEVEN-6174"