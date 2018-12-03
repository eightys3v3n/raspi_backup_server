import subprocess
import telnetlib
import getpass
from time import sleep


""" Start and stop Samba server
	Open/Close SSH connection and execute commands
	Map/Unmap network drive via SSH connection
	Run Robocopy through SSH connection to copy from Windows to Linux Samba
		Wait until complete async
		Get error code
"""


linux_ip = "192.168.1.38"
linux_username = "anonymous"
linux_password = "Abc123"
linux_path = "/mnt/shared"
windows_ip = "192.168.1.200"
windows_username = "eightys3v3n"
windows_password = getpass.getpass("Windows SSH Password: ")
windows_drive = "K:"
ssh_session = None


def StartSamba():
	subprocess.call("systemctl start smb")


def StopSamba():
	subprocess.call("systemctl stop smb")


def ConnectSSH():
	s = pxssh.pxssh()
	s.login(windows_ip, windows_username, windows_password, port="443", original_prompt="[|]")


def DisconnectSSH():
	if s is not None:
		s.logout()


def TestSSH():
	s.sendline("uptime")
	s.prompt()
	print("Tested command over SSH", s.before)


def MapNetworkDrive():
	s.sendline("net use {drive} \\\\{ip}{path} /USER:{user} {passw}".format(
		drive=windows_drive, ip=linux_ip, path=linux_path, user=linux_user, passw=linux_password))
	s.prompt()
	print("Map drive output:", s.before)


def UnmapNetworkDrive():
	s.sendline("net use \\\\{ip}{path} /delete".format(ip=linux_ip, path=linux_path))
	s.prompt()
	print("Unmap drive output:", s.before)


def BackupFiles():
	folder_name = datetime.now().__str__()
	folder_name = folder_name.sub(":", "-")
	s.sendline("/mnt/c/Windows/System32/Robocopy.exe {fr} {to} /ZB /COPYALL /MIR".format(fr=windows_folder, to=drive+"\\"+folder_name))
	s.prompt()
	print("Backup file output:", s.before)


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