# -*- coding: utf-8 -*-
import asyncio
import json
import blivedm
import sys
import aiohttp

# -----------------------------------------------------------------------------
# B站直播间原始数据捕获与分析工具
# 功能：连接指定直播间，捕获 WebSocket 推送的原始 JSON 数据并打印，
#       用于分析协议字段、点赞、@提及等未封装信息。
# -----------------------------------------------------------------------------

class RawDebugHandler(blivedm.BaseHandler):
    def handle(self, client: blivedm.BLiveClient, command: dict):
        """
        拦截并处理所有 WebSocket 消息
        :param client: 客户端实例
        :param command: 原始 JSON 数据字典
        """
        cmd = command.get('cmd', '')
        
        # 过滤掉一些高频且通常不关注的心跳或无关消息（可选）
        # if cmd in ['STOP_LIVE_ROOM_LIST', 'WATCHED_CHANGE']:
        #     return

        print(f"\n{'='*20} 收到指令: {cmd} {'='*20}")
        
        # 1. 打印原始 JSON 数据（格式化输出）
        print(json.dumps(command, ensure_ascii=False, indent=2))
        
        # 2. 简单拆解分析常见指令
        self.analyze_command(cmd, command)

        # 3. 调用父类方法，确保 blivedm 内部逻辑正常运行（如心跳保持）
        super().handle(client, command)

    def analyze_command(self, cmd: str, command: dict):
        """对常见指令进行字段拆解分析"""
        data = command.get('data', {})
        info = command.get('info', [])

        if cmd == 'DANMU_MSG':
            # 弹幕消息
            # info[0]: 弹幕元数据 (包含部分用户属性)
            # info[1]: 弹幕内容
            # info[2]: 用户信息 [uid, uname, isAdmin, isVip, isSvip, rank, ...]
            # info[3]: 勋章信息
            print(f"  [分析] 弹幕内容: {info[1]}")
            print(f"  [分析] 发送用户: {info[2][1]} (UID: {info[2][0]})")
            # 尝试解析 @ 引用 (仅作示例，实际需根据业务逻辑细化)
            if '@' in info[1]:
                 print(f"  [分析] *** 检测到可能的 @ 引用 ***")

        elif cmd == 'SEND_GIFT':
            # 礼物消息
            print(f"  [分析] 礼物名称: {data.get('giftName')}")
            print(f"  [分析] 用户: {data.get('uname')} (操作: {data.get('action')})")
            print(f"  [分析] 数量: {data.get('num')} | 价格: {data.get('price')}")

        elif cmd == 'INTERACT_WORD':
            # 互动消息 (进入直播间、关注)
            msg_type = data.get('msg_type')
            action = "进入直播间" if msg_type == 1 else "关注直播间"
            print(f"  [分析] 交互: {data.get('uname')} {action}")

        elif cmd == 'LIKE_INFO_V3_CLICK':
            # 点赞消息
            print(f"  [分析] 点赞: {data.get('uname')} {data.get('like_text')}")

        elif cmd == 'GUARD_BUY':
            # 上舰消息
            print(f"  [分析] 上舰: {data.get('username')} 购买了 {data.get('gift_name')}")

        elif cmd == 'SUPER_CHAT_MESSAGE':
            # SC 醒目留言
            print(f"  [分析] SC({data.get('price')}元): {data.get('user_info', {}).get('uname')} 说: {data.get('message')}")

async def main():
    # 获取房间号参数，默认为一个热门房间
    room_id = 7777
    sessdata = None

    if len(sys.argv) > 1:
        try:
            room_id = int(sys.argv[1])
        except ValueError:
            print("错误: 房间号必须是整数")
            return
            
    sessdata = '57f63751%2C1781198918%2C098dd%2Ac2CjAcRQOyP5QQELegf-mWjwOVLxv2NITbEu9-98DVwefuF-3-2udFjZ7iS4qQ8LkMzaESVkdqQVZxU0h0UlRhZ1lPWUx6U2dnNnJCck5iZTZMMF8tREpCMm9QWDBvZTJwV1Q2ZXJ3bk0zQXVmZ0xkZTNVc2VjZkVra1VXQUNsc3RNbGVPMUNzTmVnIIEC'

    print(f"正在连接直播间: {room_id} ...")
    if sessdata:
        print("已启用身份验证 (SESSDATA)")
    else:
        print("未提供 SESSDATA，使用匿名连接 (可能缺少部分数据)")
        
    print("按 Ctrl+C 停止捕获")

    # 如果提供了 SESSDATA，则创建带 Cookie 的 session
    session = None
    if sessdata:
        cookies = {'SESSDATA': sessdata}
        session = aiohttp.ClientSession(cookies=cookies, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})

    try:
        client = blivedm.BLiveClient(room_id, session=session)
        handler = RawDebugHandler()
        client.set_handler(handler)
    
        client.start()
        await client.join()
    except KeyboardInterrupt:
        print("停止捕获")
    finally:
        await client.stop()
        if session:
            await session.close()

if __name__ == '__main__':
    asyncio.run(main())
