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
linux_path = "backups"
windows_ip = "192.168.1.200"
windows_username = "Terrence"
windows_password = getpass.getpass("Windows SSH Password: ")
# windows_password = "Abc123"
windows_drive = "K:"
windows_folder = "C:\\Users\\Terrence\\Desktop\\test"
ssh_session = None


share_path = "\"\\\\{}\\{}\"".format(linux_ip, linux_path)
# folder_name = datetime.now().__str__().replace(':', '-').replace(' ', '_')
folder_name = "test"
backup_dst = "{drive}\\{folder_name}".format(drive=windows_drive, folder_name=folder_name)


def StartSamba():
	subprocess.call("/usr/bin/systemctl start smb", shell=True)


def StopSamba():
	subprocess.call("/usr/bin/systemctl stop smb", shell=True)


def ConnectSSH():
	global ssh_session
	ssh_session = pxssh.pxssh()
	ssh_session.login(windows_ip, windows_username, windows_password, port="443", original_prompt="[>$]", auto_prompt_reset=False)
	# ssh_session.sync_original_prompt(sync_multiplier=1)
	ssh_session.setwinsize(20, 200)


def DisconnectSSH():
	if ssh_session is not None:
		ssh_session.logout()


def MapNetworkDrive():
	cmd = "net use {drive} {share} /USER:{user} {passw}".format(
		drive=windows_drive, share=share_path, user=linux_username, passw=linux_password)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	if b"The command completed successfully" not in ssh_session.before:
		print("Map drive output:", ssh_session.before.decode())

def UnmapNetworkDrive():
	cmd = "net use {} /delete".format(share_path)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	if b"The command completed successfully" not in ssh_session.before:
		print("Unmap drive output failed:", ssh_session.before.decode())


def BackupFiles():
	cmd = "robocopy \"{from_}\" \"{to}\" /ZB /MIR /COPY:DAT".format(from_=windows_folder, to=backup_dst)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	print(ssh_session.before.decode())


def DoBackup():
	# print("Starting Samba")
	# StartSamba()
	print("Connecting SSH")
	ConnectSSH()
	print("Mapping drive")
	MapNetworkDrive()
	print("Backing up files")
	BackupFiles()
	print("Unmapping drive")
	UnmapNetworkDrive()
	# print("Disconnecting SSH")
	# DisconnectSSH()
	# print("Stopping Samba")
	# StopSamba()


def main():
	DoBackup()


if __name__ == '__main__':
	main()