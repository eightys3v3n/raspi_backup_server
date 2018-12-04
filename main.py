import subprocess
from pexpect import pxssh
import getpass
from time import sleep
from datetime import datetime


""" Start and stop Samba server
	Open/Close SSH connection and execute commands
	Map/Unmap network drive via SSH connection
	Run Robocopy through SSH connection to copy from Windows to Linux Samba
		Wait until complete async
		Get error code
"""

""" CURRENTLY
	The drive will not map on the windows PC using MapNetworkDrive()
"""


linux_ip = "192.168.1.38"
linux_username = "anonymous"
linux_password = "Abc123"
# linux_path = "/mnt/{drive}/shared/{folder}"
linux_path = "backups"
windows_ip = "192.168.1.200"
windows_username = "eightys3v3n"
windows_password = getpass.getpass("Windows SSH Password: ")
windows_drive = "K:"
# windows_folder = "/mnt/c/Users/Terrence/Desktop/test"
windows_folder = "C:\\Users\\Terrence\\Desktop\\test"
ssh_session = None


def StartSamba():
	subprocess.call("/usr/bin/systemctl start smb", shell=True)


def StopSamba():
	subprocess.call("/usr/bin/systemctl stop smb", shell=True)


def ConnectSSH():
	global ssh_session
	ssh_session = pxssh.pxssh()
	ssh_session.login(windows_ip, windows_username, windows_password, port="443", original_prompt="[|]")


def DisconnectSSH():
	if ssh_session is not None:
		ssh_session.logout()


def TestSSH():
	ssh_session.sendline("uptime")
	ssh_session.prompt()
	print("Tested command over SSH", ssh_session.before)


def MapNetworkDrive():
	print("/mnt/c/Windows/System32/net.exe use {drive} \\\\{ip}\\{path} /USER:{user} {passw}".format(
		drive=windows_drive, ip=linux_ip, path=linux_path, user=linux_username, passw=linux_password))
	ssh_session.sendline("/mnt/c/Windows/System32/net.exe use {drive} \\\\{ip}\\{path} /USER:{user} {passw}".format(
		drive=windows_drive, ip=linux_ip, path=linux_path, user=linux_username, passw=linux_password))
	ssh_session.prompt()
	print("Map drive output:", ssh_session.before)


def UnmapNetworkDrive():
	ssh_session.sendline("/mnt/c/Windows/System32/net.exe use {drive} /delete".format(drive=windows_drive))
	ssh_session.prompt()
	print("Unmap drive output:", ssh_session.before)


def BackupFiles():
	folder_name = datetime.now().__str__()
	folder_name = folder_name.replace(":", "-")
	drive = windows_drive.lower()[0]
	path = linux_path.format(drive=drive, folder="test")
	# ssh_session.sendline("rsync -raAX {fr} {to}".format(fr=windows_folder, to=path))
	ssh_session.sendline("/mnt/c/Windows/System32/Robocopy.exe {fr} {to} /ZB /COPYALL /MIR".format(fr=windows_folder, to=path))
	ssh_session.prompt()
	print("Backup file output:", ssh_session.before)


def DoBackup():
	print("Starting Samba")
	StartSamba()
	print("Connecting SSH")
	ConnectSSH()
	print("Mapping drive")
	MapNetworkDrive()
	print("Backing up files")
	BackupFiles()
	print("Unmapping drive")
	UnmapNetworkDrive()
	print("Disconnecting SSH")
	DisconnectSSH()
	print("Stopping Samba")
	StopSamba()


def main():
	while True:
		DoBackup()
		sleep(60)


if __name__ == '__main__':
	main()