import io
import re
import base64
import requests
from PIL import Image
import qrcode

global_cookies = ""
global_bili_jct = ""
login_session = None


def get_qr():
    global login_session
    try:
        login_session = requests.session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        resp = login_session.get(
            'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header',
            headers=headers).json()
        if resp['code'] != 0:
            return False, "获取二维码失败", None

        login_url = resp['data']['url']
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(login_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((200, 200), Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        qr_data_url = f"data:image/png;base64,{img_str}"

        return True, "", {
            'qr_url': qr_data_url,
            'login_url': login_url,
            'qrcode_key': resp['data']['qrcode_key']
        }
    except Exception as e:
        return False, f'获取二维码失败: {str(e)}', None


def poll(qrcode_key: str):
    global global_cookies, global_bili_jct, login_session
    try:
        if not qrcode_key or not login_session:
            return False, "无效的登录会话", None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        token_url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header'
        qrcode_data = login_session.get(token_url, headers=headers).json()

        if qrcode_data['data']['code'] == 0:
            login_session.get(qrcode_data['data']['url'], headers=headers)
            global_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in login_session.cookies])
            bili_jct_match = re.findall(r'bili_jct=(.*?)(;|$)', global_cookies)
            global_bili_jct = bili_jct_match[0][0] if bili_jct_match else ""
            return True, "登录成功", {'status': 'success'}
        else:
            return True, "", {'status': 'waiting', 'message': qrcode_data['data']['message']}
    except Exception as e:
        return False, f'轮询登录状态失败: {str(e)}', None


def status():
    global global_cookies, login_session
    try:
        if not global_cookies or not login_session:
            return True, "", {'logged_in': False}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
        }
        url = 'https://api.bilibili.com/x/web-interface/nav'
        resp = login_session.get(url=url, headers=headers).json()

        if resp['data']['isLogin']:
            return True, "", {
                'logged_in': True,
                'user_info': {
                    'username': resp['data']['uname'],
                    'face': resp['data']['face'],
                    'uid': resp['data']['mid'],
                    'level': resp['data']['level_info']['current_level'],
                    'vip_type': resp['data']['vipType'],
                    'vip_status': resp['data']['vipStatus']
                }
            }
        else:
            return True, "", {'logged_in': False}
    except Exception as e:
        return False, f'获取登录状态失败: {str(e)}', None


def logout():
    global global_cookies, global_bili_jct, login_session
    try:
        if global_bili_jct:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81',
            }
            url = 'https://passport.bilibili.com/login/exit/v2'
            data = {'biliCSRF': global_bili_jct}
            requests.post(url, headers=headers, data=data)
        global_cookies = ""
        global_bili_jct = ""
        login_session = None
        return True, "已注销登录"
    except Exception as e:
        return False, f'注销失败: {str(e)}'