#!/usr/bin/env python3
#-------------------------------------------------------------
# 以下区域是我的代码
'''

【项目简介】 网络聊天室 v0.0.2

【加入项目】
注意代码只添加不修改，你可以写个函数，署名
不要修改别人的代码。

【基线规则】
在自己的区域修改代码，谁的代码能跑就加入主线
除此之外只在各自的测试区域内运行

【设计思路】
建议一个项目一个文件先，容易分发

【测试方式】
服务器进程： python chat.py --type=server
客户端进程： python chat.py

--------------------------------
--------------------------------
--------------------------------
【项目名称】 网络聊天室 v 0.0.3 （20250524）
我们会将新版本加入pmc.cops中作为常驻服务

【改进计划】
1.我们专门设置了一个只发送一条消息就关闭的函数以供别的文件调用
2.我们将端口暴露在了公网下，以测试连接情况，发现并修复了许多bug。
3.我们设置欢迎信息只在服务端可见。

【使用方法】
python chat.py [--type=server|client] [--addr=localhost] [--port=8003] [--name=Unknow]

【记得反馈！】
期待您将反馈发送至gitee

----------------------------------------
########################################
########################################

网络聊天室 version 0.1.0

使用方法 python chat.py [--addr=localhost] [--port=8003] [--name=Unknow]
'''
import argparse
import socket
import select
import threading
import sys
import time


class ChatClient:
    def __init__(self, addr: str, port: int, your_name: str):
        self.addr: str = addr
        self.port: int = port
        self.name: str = your_name

    def send_client(self, msg: str):
        '''发送消息给聊天室服务器。'''
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.addr, self.port))
                s.sendall(f"{self.name}: {msg}".encode('utf-8'))
        except ConnectionRefusedError:
            print(f"Could not connect to {self.addr}:{self.port}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def recv_loop(self, s: socket.socket):
        """
        接收消息的函数，持续从服务器接收消息并打印。
        Args:
            s (socket.socket): 连接的套接字对象

        使用select监视套接字状态，当套接字可读时接收消息并打印。
        """
        socklist = [s]
        while self.running:
            
            try:
                readable, _, exception = select.select(socklist, [], socklist, 0.1) 

                if readable != []:

                    try:
                        msg = readable[0].recv(8092)
                        if msg: print(msg.decode('utf-8'))
                    except ConnectionResetError:
                        print("Connection closed by server.")
                        break

                if exception != []:
                    print("Exception on socket, closing...")
                    break

            except ValueError:
                ... # 程序退出了会抛出这个异常


    def _lexer(self, input_data: str):
        '''如果不需要发送则返回None。'''
        if input_data == "quit":
            self.running = False
            return None
        elif not self.extra_cmd and input_data == "chatgpt":
            self.extra_cmd = "<chatgpt>"
            return None
        elif self.extra_cmd and input_data == "del":
            self.extra_cmd = None
            return None
        elif input_data == "where":
            print(f'---{self.extra_cmd}---')
            return None
        else:
            return input_data
    
    def _mixup_msg(self, input_data):
        if self.extra_cmd:
            return f"{self.extra_cmd}{input_data}"
        else:
            return input_data
            
    def send_p(self,):
        '''读取并且发送消息的进程'''
        self.extra_cmd = None
        while self.running:
            try:
                # 使用input()替代select.select()，更兼容Windows
                input_data = input().strip()
                input_data = self._lexer(input_data)
                if input_data: # 如果不需要发送，_lexer返回None
                    input_data = self._mixup_msg(input_data)
                    self.send_client(input_data)
            except EOFError:
                # 处理Ctrl+D等情况
                break
            except Exception as e:
                # 捕获其他异常，防止程序崩溃
                print(f"Input error: {e}")
                continue

    def _connect_and_print(self, s: socket.socket):
        s.connect((self.addr, self.port))
        print(f'Connected to {self.addr}:{self.port}')

    def _sleep_if_reconnect(self, second: int):
        if self.running:
            print("prepare to reconnect...")
            time.sleep(second)

    def recv_client(self):
        """客户端主函数，建立与服务器的连接并管理消息收发"""
        self.running = True
        self.th = threading.Thread(target=self.send_p)
        self.th.start()
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    self._connect_and_print(s)
                    self.recv_loop(s)
            except ConnectionRefusedError:
                print(f"Could not connect to {self.addr}:{self.port}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            
            self._sleep_if_reconnect(1)

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='聊天室配置。')
    parser.add_argument('--addr', type=str, default='qsont.xyz', help='选择要连接的地址')
    parser.add_argument('--port', type=int, default=8003, help='选择要连接的地址')
    parser.add_argument('--name', type=str, default='Unknow', help='你的名字是什么')
    args = parser.parse_args()
    client = ChatClient(args.addr, args.port, args.name)
    client.recv_client()

if __name__ == "__main__":
    main()

