#!/usr/bin/env python3
"""远程检查龙芯机器环境并上传编译推箱子游戏"""
import paramiko
import os
import sys
import stat

HOST = '192.168.31.13'
USER = 'whj'
PASS = '1'
REMOTE_DIR = '/home/whj/sokoban'
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

def ssh_exec(ssh, cmd):
    """执行远程命令并打印输出"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    print(f'>>> {cmd}')
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print(f'[stderr] {err.rstrip()}')
    if code != 0:
        print(f'[exit code: {code}]')
    print()
    return code

def upload_dir(sftp, local, remote):
    """递归上传目录"""
    # 创建远程目录
    try:
        sftp.stat(remote)
    except IOError:
        sftp.mkdir(remote)

    for item in os.listdir(local):
        local_path = os.path.join(local, item)
        remote_path = remote + '/' + item
        if os.path.isdir(local_path):
            # 跳过 __pycache__ 等
            if item.startswith('__') or item == '.git':
                continue
            upload_dir(sftp, local_path, remote_path)
        else:
            # 跳过 .pyc, .o 等
            if item.endswith(('.pyc', '.o', '.exe')):
                continue
            print(f'  上传 {item}')
            sftp.put(local_path, remote_path)

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f'连接 {HOST}...')
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    print('连接成功\n')

    # 1. 检查环境
    print('=== 检查环境 ===')
    ssh_exec(ssh, 'which gcc && gcc --version | head -1')
    ssh_exec(ssh, 'ls /usr/include/ncurses.h /usr/include/ncursesw/ncurses.h 2>/dev/null')
    ssh_exec(ssh, 'find /usr -name "libncursesw*" 2>/dev/null | head -5')
    ssh_exec(ssh, 'dpkg -l 2>/dev/null | grep -i ncurses')

    # 2. 创建远程目录
    print('=== 创建远程目录 ===')
    ssh_exec(ssh, f'mkdir -p {REMOTE_DIR}/lib/cjson')

    # 3. 上传文件
    print('=== 上传文件 ===')
    sftp = ssh.open_sftp()
    upload_dir(sftp, LOCAL_DIR, REMOTE_DIR)
    sftp.close()
    print('上传完成\n')

    # 4. 编译
    print('=== 编译 ===')
    ssh_exec(ssh, f'cd {REMOTE_DIR} && make clean 2>/dev/null; make -j4')

    # 5. 检查编译结果
    print('=== 检查编译结果 ===')
    ssh_exec(ssh, f'ls -la {REMOTE_DIR}/sokoban 2>/dev/null && file {REMOTE_DIR}/sokoban')

    ssh.close()
    print('完成!')

if __name__ == '__main__':
    main()
