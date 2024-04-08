import socket
import socks

class ProxyCheck:

    def __init__(self):
        pass


    async def check_socket_proxy(self, hostname, port, user_name, password):
        proxy = (socks.SOCKS5, hostname, port, True, user_name, password)
        socket.socket = socks.socksocket  # 使用代理连接Socket
        try:
            # 创建Socket连接
            with socket.create_connection(("www.google.com", 80), proxy=proxy) as sock:
                print("Proxy is working!")
                return True
        except Exception as e:
            print(f"Proxy is not working: {e}")
            return False
        # pass


    async def check_mt_proxy(self, hostname, port, secret):
        try:
            # 创建Socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)  # 设置超时时间为5秒

            # 尝试连接到MTProxy服务器
            sock.connect((hostname, port))

            # 连接成功，代理可用
            print("MTProxy代理可用！")
            return True
        except Exception as e:
            # 连接失败，代理不可用
            print(f"MTProxy代理不可用：{e}")
            return False
        finally:
            # 关闭Socket连接
            sock.close()
        pass