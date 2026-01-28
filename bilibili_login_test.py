import time
import requests
import os
import sys

# Bilibili API URLs
QR_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
QR_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"

# User-Agent is important
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
}

def get_qrcode():
    """获取登录二维码URL和key"""
    try:
        response = requests.get(QR_GENERATE_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if data["code"] == 0:
            return data["data"]["url"], data["data"]["qrcode_key"]
        else:
            print(f"获取二维码失败: {data['message']}")
            return None, None
    except Exception as e:
        print(f"请求发生错误: {e}")
        return None, None

def show_qrcode(url):
    """生成并展示二维码"""
    # 使用第三方API生成二维码图片
    # 注意：URL需要编码，但requests会自动处理参数
    qr_api = "https://api.qrserver.com/v1/create-qr-code/"
    params = {
        "size": "300x300",
        "data": url
    }
    
    print("正在生成二维码...")
    try:
        response = requests.get(qr_api, params=params)
        response.raise_for_status()
        
        filename = "bilibili_login_qrcode.png"
        with open(filename, "wb") as f:
            f.write(response.content)
            
        print(f"二维码已保存为 {filename}")
        print("正在打开二维码图片，请使用哔哩哔哩手机App扫码登录...")
        
        # Windows下打开图片
        if sys.platform == "win32":
            os.startfile(os.path.abspath(filename))
        else:
            print(f"请手动打开 {filename} 进行扫码")
            
        return filename
    except Exception as e:
        print(f"生成/展示二维码失败: {e}")
        print(f"请手动生成二维码，内容为: {url}")
        return None

def poll_status(qrcode_key):
    """轮询登录状态"""
    url = f"{QR_POLL_URL}?qrcode_key={qrcode_key}"
    
    print("开始监听扫码状态...")
    
    while True:
        try:
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            
            if data["code"] == 0:
                code = data["data"]["code"]
                
                if code == 0:
                    print("\n=== 登录成功! ===")
                    print(f"Refresh Token: {data['data']['refresh_token']}")
                    # 解析并打印 Cookies
                    # 实际上返回的 url 中包含了 cookies，或者 response headers 里有 set-cookie
                    # Bilibili 现在的接口成功后，data['data']['url'] 里有跨域登录的 url，里面带了参数
                    # 但通常我们也需要提取 cookies
                    
                    # 尝试从 response cookies 获取 (如果 requests 自动处理了)
                    # 或者从 data['data'] 里获取，通常这里会有直接的 cookie 信息如果是在 web 端
                    # 观察 data['data'] 结构: {"url": "...", "refresh_token": "...", "timestamp": ..., "code": 0, "message": ""}
                    # 关键的 SESSDATA 等通常在 Set-Cookie header 里，或者需要解析返回的 url 参数
                    
                    # 修正：poll 接口返回成功时，requests 的 session 会自动管理 cookies 吗？
                    # requests.get 是无状态的，除非用 session。
                    # 但 poll 接口本身会在 Set-Cookie 中返回 SESSDATA 吗？
                    # 根据 Bilibili API 文档，poll 接口成功时，响应头里会有 Set-Cookie。
                    
                    cookies = response.cookies.get_dict()
                    print("Cookies 获取成功:")
                    for k, v in cookies.items():
                        print(f"{k}: {v}")
                    
                    if 'SESSDATA' in cookies:
                        print(f"\nSESSDATA: {cookies['SESSDATA']}")
                        return cookies
                    else:
                        print("\n警告: 未在 Cookies 中找到 SESSDATA，尝试从返回数据中分析...")
                        # 有时候需要显式提取
                        return cookies
                        
                elif code == 86101:
                    # 未扫码
                    print(".", end="", flush=True)
                elif code == 86090:
                    # 已扫码，未确认
                    print("\n已扫码，请在手机上点击确认登录...", end="", flush=True)
                elif code == 86038:
                    print("\n二维码已过期，请重新运行脚本。")
                    return None
                else:
                    print(f"\n未知状态码: {code}, 信息: {data['data']['message']}")
            else:
                print(f"\n请求失败: {data['message']}")
                
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return None
        except Exception as e:
            print(f"\n轮询发生错误: {e}")
            time.sleep(2)

def main():
    print("=== Bilibili 扫码登录测试脚本 ===")
    
    # 1. 获取二维码
    url, qrcode_key = get_qrcode()
    if not url:
        return
        
    print(f"获取二维码成功，Key: {qrcode_key}")
    
    # 2. 展示二维码
    img_file = show_qrcode(url)
    
    # 3. 轮询状态
    try:
        cookies = poll_status(qrcode_key)
        
        if cookies:
            print("\n登录流程结束。")
            # 可以选择保存 cookies 到文件
            with open("bilibili_cookies.txt", "w") as f:
                f.write(str(cookies))
            print("Cookies 已保存到 bilibili_cookies.txt")
            
    finally:
        # 清理临时图片
        if img_file and os.path.exists(img_file):
            try:
                os.remove(img_file)
                pass # 暂时保留以便查看，或者如果进程占用可能删不掉
            except:
                pass

if __name__ == "__main__":
    main()
