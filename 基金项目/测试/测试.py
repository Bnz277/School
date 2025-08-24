import os
import re
import subprocess
from urllib.parse import unquote
import requests
from time import sleep
from tkinter import StringVar, Tk, messagebox, Entry
from io import BytesIO
from PIL import Image, ImageTk
from qrcode import QRCode
from tkinter.ttk import Button, Label, Frame
from threading import Thread

# 全局变量
global_cookies = ""
global_bili_jct = ""
login_session = None


def extract_bvid(url):
    """从URL中提取BV号"""
    if "b23.tv" in url:
        try:
            url = requests.get(url, allow_redirects=False).headers.get('location', url)
        except:
            pass
    match = re.search(r'(BV[0-9A-Za-z]+)', url)
    if not match:
        raise ValueError("URL中未找到有效的BV号")
    return match.group(1)


def get_video_info(video_url, cookie=""):
    try:
        bvid = extract_bvid(video_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if cookie:
            headers["Cookie"] = cookie

        # 获取视频基本信息
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        info = requests.get(info_url, headers=headers, timeout=10).json()
        if info['code'] != 0:
            raise ValueError(f"获取视频信息失败: {info.get('message')}")

        cid = info['data']['cid']
        title = re.sub(r'[\\/:*?"<>|]', '', unquote(info['data']['title']))

        # 获取播放信息
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=4048"
        playinfo = requests.get(play_url, headers=headers, timeout=10).json()
        if playinfo['code'] != 0:
            raise ValueError(f"获取播放信息失败: {playinfo.get('message')}")

        return bvid, title, playinfo
    except Exception as e:
        raise ValueError(f"获取视频信息时出错: {str(e)}")


def select_quality(playinfo, logged_in=False):
    print("\n可选清晰度:")
    qualities = playinfo['data']['support_formats']

    # 过滤非登录用户不能选择的清晰度
    if not logged_in:
        qualities = [q for q in qualities if q['quality'] <= 80]  # 80是普通1080P

    for i, q in enumerate(qualities):
        print(f"{i + 1}. {q['new_description']} (id={q['quality']})")

    while True:
        try:
            choice = int(input("请选择清晰度(输入序号): ")) - 1
            if 0 <= choice < len(qualities):
                return qualities[choice]['quality']
            print("序号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")


def download_file(url, filename, headers):
    print(f"\n正在下载: {filename}")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = downloaded / total_size * 100
                            print(f"\r进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {str(e)}")
        return False


def merge_video_audio(video_path, audio_path, output_path):
    print("\n开始合并音视频...")
    try:
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            output_path
        ]
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo,
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print("合并完成!")
        os.remove(video_path)
        os.remove(audio_path)
        print("已删除临时音视频文件")
        return True
    except subprocess.CalledProcessError as e:
        print(f"合并失败: {str(e)}")
        print("请确保已安装ffmpeg并添加到系统PATH中")
        return False
    except Exception as e:
        print(f"合并过程中出错: {str(e)}")
        return False


def scan_code(session):
    global global_cookies, global_bili_jct, tk_image
    try:
        get_login = session.get(
            'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header',
            headers=headers).json()
        qrcode_key = get_login['data']['qrcode_key']

        qr = QRCode()
        qr.add_data(get_login['data']['url'])
        img = qr.make_image()
        pil_image_change = img.resize((200, 200), resample=Image.BICUBIC, box=None, reducing_gap=None)
        tk_image = ImageTk.PhotoImage(pil_image_change)

        token_url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header'
        v1.set('等待扫码')
        label_code.config(image=tk_image)

        while True:
            qrcode_data = session.get(token_url, headers=headers).json()
            if qrcode_data['data']['code'] == 0:
                v1.set('扫码成功')
                session.get(qrcode_data['data']['url'], headers=headers)
                break
            else:
                v1.set(qrcode_data['data']['message'])
            sleep(1)

        # 保存 Cookie 到全局变量
        global_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
        global_bili_jct = re.findall(r'bili_jct=(.*?)(;|$)', global_cookies)[0][0]
        v1.set("登录成功！")
        update_login_status(True)

    except Exception as e:
        print(f"扫码登录过程中出错: {e}")
        v1.set("登录出错，请重试")


def bz_login():
    global login_session
    login_session = requests.session()
    scan_code(login_session)


def verification():
    try:
        url = 'https://api.bilibili.com/x/web-interface/nav'
        resp1 = login_session.get(url=url, headers=headers).json()
        global tk_image

        if resp1['data']['isLogin']:
            face_url = resp1['data']['face']
            image_bytes = requests.get(face_url).content
            data_stream = BytesIO(image_bytes)
            pil_image = Image.open(data_stream)
            pil_image_change = pil_image.resize((200, 200), resample=Image.BICUBIC, box=None, reducing_gap=None)
            tk_image = ImageTk.PhotoImage(pil_image_change)
            v1.set("登录成功！")
            label_code.config(image=tk_image)
            update_login_status(True)
        else:
            thread_it(bz_login)
    except Exception as e:
        print(f"验证登录状态时出错: {e}")
        v1.set("验证出错，请重试")


def update_login_status(logged_in):
    if logged_in:
        btn_login.config(state='disabled')
        btn_logout.config(state='normal')
        btn_download.config(text='下载视频(已登录)')
    else:
        btn_login.config(state='normal')
        btn_logout.config(state='disabled')
        btn_download.config(text='下载视频(未登录)')


def thread_it(func, *args):
    thread = Thread(target=func, args=args, daemon=True)
    thread.start()


def cancel_login():
    global global_cookies, global_bili_jct
    msg1 = messagebox.askyesno(title="提示", message="确定要注销登录吗？")
    if msg1:
        try:
            if global_bili_jct:
                url3 = 'https://passport.bilibili.com/login/exit/v2'
                data3 = {'biliCSRF': global_bili_jct}
                requests.post(url3, headers=headers, data=data3).json()
            global_cookies = ""
            global_bili_jct = ""
            v1.set("已注销登录")
            white_image = Image.new('RGB', (200, 200), (256, 256, 256))
            tk_image = ImageTk.PhotoImage(white_image)
            label_code.config(image=tk_image)
            update_login_status(False)
        except Exception as e:
            print(f"注销登录时出错: {e}")
            v1.set("注销出错")


def download_video():
    global global_cookies
    video_url = url_entry.get().strip()
    if not video_url:
        messagebox.showerror("错误", "请输入视频URL！")
        return

    try:
        logged_in = bool(global_cookies)
        bvid, title, playinfo = get_video_info(video_url, global_cookies if logged_in else "")
        print(f"视频标题: {title}")

        quality_id = select_quality(playinfo, logged_in)
        video_stream = next(
            (stream for stream in playinfo['data']['dash']['video']
             if stream['id'] == quality_id),
            playinfo['data']['dash']['video'][0]
        )
        audio_stream = playinfo['data']['dash']['audio'][0]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}"
        }
        if logged_in:
            headers["Cookie"] = global_cookies

        os.makedirs("downloads", exist_ok=True)
        base_name = f"downloads/{title}"
        temp_video = f"{base_name}_video.mp4"
        temp_audio = f"{base_name}_audio.mp3"
        final_output = f"{base_name}.mp4"

        if download_file(video_stream['baseUrl'], temp_video, headers):
            if download_file(audio_stream['baseUrl'], temp_audio, headers):
                if merge_video_audio(temp_video, temp_audio, final_output):
                    messagebox.showinfo("成功", f"视频下载完成:\n{final_output}")
                else:
                    messagebox.showwarning("警告", "自动合并失败，请手动合并")
    except Exception as e:
        messagebox.showerror("错误", f"下载失败: {str(e)}")


if __name__ == '__main__':
    # 初始化 GUI
    root = Tk()
    v1 = StringVar()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
    }

    # 设置窗口
    root.geometry('350x400')
    root.title("B站视频下载器")

    # URL输入框
    url_frame = Frame(root)
    url_frame.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
    Label(url_frame, text="视频URL:").pack(side="left")
    url_entry = Entry(url_frame, width=30)
    url_entry.pack(side="left", fill="x", expand=True)

    # 按钮区域
    btn_frame = Frame(root)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
    btn_login = Button(btn_frame, text='扫码登录', command=lambda: thread_it(bz_login))
    btn_login.pack(side="left", padx=5)
    btn_logout = Button(btn_frame, text='注销登录', command=cancel_login, state='disabled')
    btn_logout.pack(side="left", padx=5)
    btn_download = Button(root, text='下载视频(未登录)', command=lambda: thread_it(download_video))
    btn_download.grid(row=2, column=0, columnspan=2, pady=5)

    # 状态标签
    label_status = Label(root, textvariable=v1)
    label_status.grid(row=3, column=0, columnspan=2, pady=5)

    # 二维码显示区域
    white_image = Image.new('RGB', (200, 200), (256, 256, 256))
    tk_image = ImageTk.PhotoImage(white_image)
    label_code = Label(root, image=tk_image)
    label_code.grid(row=4, column=0, columnspan=2, pady=5)

    root.mainloop()