import subprocess
from network_share import Samba
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


linux_ip = "192.168.1.38" # IP address of the Linux machine that will hold the backups and run this script
linux_username = "anonymous" # User name of Samba share hosted on Linux machine
linux_password = "Abc123" # Password of Samba share hosted on Linux machine
linux_path = "backups" # The name of the share; the part in the square brackets in smb.conf
windows_ip = "192.168.1.200" # The IP address of the Windows server to be backed up
windows_ssh_port = 443 # Port of the SSH server on the Windows machine
windows_username = "Terrence" # User name to login as on the Windows machine
windows_password = getpass.getpass("Windows SSH Password: ") # Password to login to Windows machine with | This is the same as the user password
# windows_password = "Abc123" # If you want to hard-code the password comment the above line and uncomment this one. VERY UNRECOMMENDED AND POOR SECURITY PRACTICE.
windows_drive = "K:" # What drive letter to use when mounting the network share
windows_folder = "C:\\Users\\Terrence\\Desktop\\test" # What folder to backup


# These are derived from the above variables.
share_path = "\"\\\\{}\\{}\"".format(linux_ip, linux_path)
folder_name = datetime.now().__str__().replace(':', '-').replace(' ', '_')
# folder_name = "test"
backup_dst = "{drive}\\{folder_name}".format(drive=windows_drive, folder_name=folder_name)

ssh_session = None


def ConnectSSH():
	""" Create a new SSH connection and attempt to login to the Windows server.
	"""
	global ssh_session
	ssh_session = pxssh.pxssh()
	ssh_session.login(windows_ip, windows_username, windows_password, port=windows_ssh_port, original_prompt="[>$]", auto_prompt_reset=False)
	# ssh_session.sync_original_prompt(sync_multiplier=1)
	ssh_session.setwinsize(20, 200)


def DisconnectSSH():
	""" Disconnect from the Windows server.
	"""
	if ssh_session is not None:
		ssh_session.logout()
	ssh_session = None


def MapNetworkDrive():
	""" Map the network share on the Windows machine using a command prompt command via the SSH connection.
		Prints the output of the command if it doesn't contain "The command completed successfully".
	"""
	cmd = "net use {drive} {share} /USER:{user} {passw}".format(
		drive=windows_drive, share=share_path, user=linux_username, passw=linux_password)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	if b"The command completed successfully" not in ssh_session.before:
		print("Map drive output:", ssh_session.before.decode())

def UnmapNetworkDrive():
	""" Unmap the mapped network share.
		Prints the output of the command if it doesn't contain "The command completed successfully".
	"""
	cmd = "net use {} /delete".format(share_path)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	if b"The command completed successfully" not in ssh_session.before:
		print("Unmap drive output failed:", ssh_session.before.decode())


def BackupFiles():
	""" Use robocopy to mirror the windows_path to the share under the folder_name derived at the top.
	"""
	cmd = "robocopy \"{from_}\" \"{to}\" /ZB /MIR /COPY:DAT".format(from_=windows_folder, to=backup_dst)

	ssh_session.sendline(cmd)
	ssh_session.prompt()
	print(ssh_session.before.decode())


def DoBackup():
	""" Actually do one backup:
			- Start Samba
			- Connect over SSH to Windows
			- Map network share
			- Backup files
			- Unmap network share
			- Disconnect from SSH
			- Stop Samba
	"""
	print("Starting Samba")
	Samba.Start()
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
	Samba.Stop()


def main():
	DoBackup()


if __name__ == '__main__':
	main()