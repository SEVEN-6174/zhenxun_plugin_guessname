from nonebot import (
    on_command,
    on_fullmatch
)
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment,
    Message,
    Bot
)
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER

from typing import *
import random
import time
from pathlib import Path

datas = {}
main_path: Path = Path(__file__).resolve().parent
data_path: Path = main_path / 'song.data'

start: Type[Matcher] = on_command('开字符', priority=5, block=True)
gen: Type[Matcher] = on_command('k', aliases={'打开'}, priority=5, block=True)
check: Type[Matcher] = on_command('验证', priority=5, block=True)
check2: Type[Matcher] = on_command('c', priority=5, block=True)
stop: Type[Matcher] = on_fullmatch('结束', priority=5, block=True)


def show(txt: str, p: str, k: str) -> str:
    txt_: str = txt
    for i in range(txt.count(k)):
        mov: int = len(txt)-len(txt_)
        p = [i for i in p]
        p[txt_.index(k)+mov:txt_.index(k)+len(k)+mov] = k
        p = ''.join(p)
        txt_ = txt_[txt_.index(k)+len(k):]
    return p


@start.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()) -> None:
    global datas
    if datas.get(event.group_id, None) != None:
        await start.finish('游戏已经开始了,输入"结束"结束游戏')
    if not arg:
        num = 10
    else:
        arg: str = arg.extract_plain_text().strip()
        if arg.isdecimal():
            num = int(arg)
            if num <= 0:
                await start.finish('必须大于0哦')
        else:
            await start.finish('必须得是数字哦')
    with open(data_path, 'r', encoding='utf-8') as f:
        txts = list(set(f.read().strip().split('\n')))
    random.shuffle(txts)
    if num > len(txts):
        await start.finish('曲目太多了')
    txts: List[str] = txts[:num]
    ps: List[str] = ['*'*len(i) for i in txts]
    guess = set()
    count = 0
    for i in range(len(txts)):
        ps[i] = show(txts[i], ps[i], ' ')
    out: str = ''
    for i in range(len(ps)):
        out += f'{i+1}.{ps[i]}'
        if ps[i] != txts[i]:
            out += '\n'
        else:
            out += '✓\n'
    out = out.strip()
    datas[event.group_id] = {'txts': txts,
                             'guess': guess, 'count': count, 'ps': ps, 'times': time.time(), 'sender': event.user_id, 'hide': len(txts)>20}
    await start.finish(out)


@gen.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()) -> None:
    global datas
    mode: bool = True if datas.get(event.group_id, None) == None else False
    txts: List[str] = datas[event.group_id]['txts']
    guess: Set = datas[event.group_id]['guess']
    count: int = datas[event.group_id]['count']
    ps: List[str] = datas[event.group_id]['ps']
    times: float = datas[event.group_id]['times']
    sender: int = datas[event.group_id]['sender']
    hide: bool = datas[event.group_id]['hide']
    if (not arg) and (not mode):
        await gen.finish('开什么字符呢')
    elif (not arg) and mode:
        return
    args: str = arg.extract_plain_text().strip().split(' ')
    if any([len(i) != 1 for i in args]) and mode:
        return
    elif any([len(i) != 1 for i in args]):
        await gen.finish('每个字符的长度只能是1')
    for k in args:
        if k == '':
            continue
        count += 1
        guess.add(k)
        for i in range(len(ps)):
            ps[i] = show(txts[i], ps[i], k.lower())
            ps[i] = show(txts[i], ps[i], k.upper())
            datas[event.group_id] = {'txts': txts,
                                     'guess': guess, 'count': count, 'ps': ps, 'times': times, 'sender': sender, 'hide': hide}
    out: Literal[''] = ''
    out += '已猜'+','.join(guess)+'\n'
    for i in range(len(ps)):
        if hide and (ps[i] == txts[i]):
            continue
        out += str(i+1)+'.'
        out += ps[i]
        if ps[i] != txts[i]:
            out += '\n'
        else:
            out += '✓\n'
    if all(ps[i] == txts[i] for i in range(len(txts))):
        out += '游戏结束\n'
        out += f'总题数:{len(txts)}\n'
        out += f'猜测次数:{count}\n'
        out += f'总字符数:{sum(len(i) for i in txts)}\n'
        del datas[event.group_id]
    out = out.strip()
    await gen.finish(out)


@check.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()) -> None:
    global datas
    mode: bool = True if datas.get(event.group_id, None) == None else False
    txts: List[str] = datas[event.group_id]['txts']
    guess: Set = datas[event.group_id]['guess']
    count: int = datas[event.group_id]['count']
    ps: List[str] = datas[event.group_id]['ps']
    times: float = datas[event.group_id]['times']
    sender: int = datas[event.group_id]['sender']
    hide: bool = datas[event.group_id]['hide']
    if (not arg) and (not mode):
        await check.finish('要验证什么呢')
    elif (not arg) and mode:
        return
    args: List[str] = arg.extract_plain_text().strip().split(' ')
    while '' in args:
        args.remove('')
    if len(args) == 1 and (not mode):
        await check.finish('参数数量不符')
    elif len(args) == 1 and mode:
        return
    song_id: str = args[-1]
    if song_id.isdecimal():
        song_id = int(song_id)
    else:
        await check.finish('歌曲编号需要整数')
    song_id: int
    if song_id < 0 or song_id > len(txts):
        await check.finish('歌曲编号超出范围')
    song_name: str = ' '.join(args[:-1])
    count += 1
    ret = False
    if txts[song_id-1].lower() == song_name.lower() or txts[song_id-1].split('(')[0].strip().lower() == song_name.lower():
        ps[song_id-1] = txts[song_id-1]
        ret = True
    datas[event.group_id] = {'txts': txts,
                             'guess': guess, 'count': count, 'ps': ps, 'times': times, 'sender': sender, 'hide': hide}
    if ret:
        out: Literal[''] = ''
        out += '正确,已猜'+','.join(guess)+'\n'
        for i in range(len(ps)):
            if hide and (ps[i] == txts[i]):
                continue
            out += str(i+1)+'.'
            out += ps[i]
            if ps[i] != txts[i]:
                out += '\n'
            else:
                out += '✓\n'
        if all(ps[i] == txts[i] for i in range(len(txts))):
            out += '游戏结束\n'
            out += f'总题数:{len(txts)}\n'
            out += f'猜测次数:{count}\n'
            out += f'总字符数:{sum(len(i) for i in txts)}\n'
            del datas[event.group_id]
        out = out.strip()
        await check.finish(out)
    await check.finish('猜错了哦')


@check2.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()) -> None:
    global datas
    mode = True if datas.get(event.group_id, None) == None else False
    txts: List[str] = datas[event.group_id]['txts']
    guess: Set = datas[event.group_id]['guess']
    count: int = datas[event.group_id]['count']
    ps: List[str] = datas[event.group_id]['ps']
    times: float = datas[event.group_id]['times']
    sender: int = datas[event.group_id]['sender']
    hide: bool = datas[event.group_id]['hide']
    if (not arg) and (not mode):
        await check2.finish('要验证什么呢')
    elif (not arg) and mode:
        return
    args: List[str] = arg.extract_plain_text().strip().split('.')
    if len(args) == 1 and (not mode):
        await check2.finish('参数数量不符')
    elif len(args) == 1 and mode:
        return
    song_id: str = args[0]
    if song_id.isdecimal():
        song_id = int(song_id)
    else:
        await check2.finish('歌曲编号需要整数')
    song_id: int
    if song_id < 0 or song_id > len(txts):
        await check2.finish('歌曲编号超出范围')
    song_name: str = '.'.join(args[1:])
    count += 1
    ret = False
    if txts[song_id-1].lower() == song_name.lower() or txts[song_id-1].split('(')[0].strip().lower() == song_name.lower():
        ps[song_id-1] = txts[song_id-1]
        ret = True
    datas[event.group_id] = {'txts': txts,
                             'guess': guess, 'count': count, 'ps': ps, 'times': times, 'sender': sender, 'hide': hide}
    if ret:
        out: Literal[''] = ''
        out += '正确,已猜'+','.join(guess)+'\n'
        for i in range(len(ps)):
            if hide and (ps[i] == txts[i]):
                continue
            out += str(i+1)+'.'
            out += ps[i]
            if ps[i] != txts[i]:
                out += '\n'
            else:
                out += '✓\n'
        if all(ps[i] == txts[i] for i in range(len(txts))):
            out += '游戏结束\n'
            out += f'总题数:{len(txts)}\n'
            out += f'猜测次数:{count}\n'
            out += f'总字符数:{sum(len(i) for i in txts)}\n'
            del datas[event.group_id]
        out = out.strip()
        await check2.finish(out)
    await check2.finish('猜错了哦')


@stop.handle()
async def _(event: GroupMessageEvent) -> None:
    global datas
    mode = True if datas.get(event.group_id, None) == None else False
    txts: List[str] = datas[event.group_id]['txts']
    guess: Set = datas[event.group_id]['guess']
    count: int = datas[event.group_id]['count']
    ps: List[str] = datas[event.group_id]['ps']
    times: float = datas[event.group_id]['times']
    sender: int = datas[event.group_id]['sender']
    hide: bool = datas[event.group_id]['hide']
    if mode:
        return
    if event.user_id == sender or (time.time() - times) > len(txts) * 60:
        out = ''
        out += '已猜'+','.join(guess)+'\n'
        for i in range(len(txts)):
            out += f'{i+1}.{txts[i]}'
            if ps[i] != txts[i]:
                out += '\n'
            else:
                out += '✓\n'
        out += '游戏结束\n'
        out += f'总题数:{len(txts)}\n'
        out += f'猜测次数:{count}\n'
        out += f'总字符数:{sum(len(i) for i in txts)}\n'
        out += '未完成全部...'
        del datas[event.group_id]
        await stop.finish(out.strip())
    else:
        await stop.finish(f'请发起人结束或在游戏开始后{len(txts)}min结束')
