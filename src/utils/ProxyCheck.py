import socket
import socks
import time

class ProxyCheck:

    def __init__(self):
        pass


    def check_socket_proxy(self, hostname, port, user_name, password):
        start_time = time.time()
        try:
            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.settimeout(15)  # 设置超时时间为 5 秒
            proxy_socket.connect((hostname, port))
            # 如果需要进行认证，可以发送相应的认证信息
            proxy_socket.send(f"{user_name}:{password}".encode())
            end_time = time.time()
            proxy_socket.close()
            end_time = time.time()
            print(f'连接时间为：{end_time - start_time}')
            return end_time - start_time  # 返回连接时间
        except socket.error as e:
            print(f"连接失败：{e}")
            return -1


    def check_mt_proxy(self, hostname, port, secret):
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