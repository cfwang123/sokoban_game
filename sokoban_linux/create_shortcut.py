#!/usr/bin/env python3
"""在远程龙芯机器创建桌面快捷方式"""
import paramiko

HOST = '192.168.31.13'
USER = 'whj'
PASS = '1'

desktop_entry = """[Desktop Entry]
Name=Sokoban
Comment=推箱子控制台游戏
Exec=konsole -e bash -c 'cd /home/whj/sokoban && ./sokoban'
Icon=applications-games
Terminal=true
Type=Application
Categories=Game;
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# 写入桌面快捷方式
sftp = ssh.open_sftp()
with sftp.file('/home/whj/桌面/Sokoban.desktop', 'w') as f:
    f.write(desktop_entry)
sftp.close()

# 设置可执行权限
stdin, stdout, stderr = ssh.exec_command('chmod +x "/home/whj/桌面/Sokoban.desktop" && echo OK')
print('快捷方式:', stdout.read().decode().strip())

# 确认文件
stdin, stdout, stderr = ssh.exec_command('ls -lh /home/whj/sokoban/sokoban /home/whj/sokoban/levels.json "/home/whj/桌面/Sokoban.desktop"')
print('文件列表:')
print(stdout.read().decode().strip())

ssh.close()
print('完成!')
