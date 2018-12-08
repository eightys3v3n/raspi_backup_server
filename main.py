import subprocess
import network_share as samba
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


win_ip = "192.168.1.200" # The IP address of the Windows server to be backed up
win_user = "Terrence" # User name to login as on the Windows machine
win_pass = getpass("Windows SSH password: ") # Password to login to Windows machine with | This is the same as the user password
win_ssh_port = 443 # Port of the SSH server on the Windows machine

win_drive = "K:" # What drive letter to use when mounting the network share
win_folder = "C:\\Users\\Terrence\\Desktop\\test" # What folder to backup

linux_ip = "192.168.1.38" # IP address of the Linux machine that will hold the backups and run this script
linux_user = "anonymous" # User name of Samba share hosted on Linux machine
linux_pass = "Abc123" # Password of Samba share hosted on Linux machine
linux_path = "backups" # The name of the share; the part in the square brackets in smb.conf

prompt_regex = "[>$]" # This regex is used to detect when a command has completed on the server. It should match the prompt.

# These are derived from the above variables.
share_path = "\"\\\\{}\\{}\"".format(linux_ip, linux_path) # Share path turns into "\\192.168.1.38\backups"
folder_name = datetime.now().__str__().replace(':', '-').replace(' ', '_')[0:-7] # Name the destination folder based on the date "YYYY-MM-dd_HH-mm-ss"
backup_dst = "{drive}\\{folder_name}".format(drive=win_drive, folder_name=folder_name) # Destination path "K:\folder_name"


def ConnectSSH():
	""" Create a new SSH connection and attempt to login to the Windows server.
	"""
	ssh_sess = pxssh.pxssh()
	ssh_sess.login(win_ip, win_username, win_password, port=win_ssh_port, original_prompt=prompt_regex, auto_prompt_reset=False)
	ssh_sess.setwinsize(20, 200)
	return ssh_sess


def DisconnectSSH(ssh_sess):
	""" Disconnect from the Windows server.
	"""
	if ssh_sess is not None:
		ssh_sess.logout()


def MapNetworkDrive(ssh_sess):
	""" Map the network share on the Windows machine using a command prompt command via the SSH connection.
		Prints the output of the command if it doesn't contain "The command completed successfully".
	"""
	cmd = "net use {drive} {share} /USER:{user} {passw}".format(
		drive=win_drive, share=share_path, user=linux_user, passw=linux_pass)
	# net use K: "\\192.168.1.38\\backups" /USER:Terrence linux_pass

	ssh_sess.sendline(cmd)
	ssh_sess.prompt()
	if b"The command completed successfully" not in ssh_sess.before:
		print("Failed to map drive?\nMap drive output:", ssh_sess.before.decode())

def UnmapNetworkDrive(ssh_sess):
	""" Unmap the mapped network share.
		Prints the output of the command if it doesn't contain "The command completed successfully".
	"""
	cmd = "net use {} /DELETE".format(share_path)
	# net use \\192.168.1.38\\backups /DELETE

	ssh_sess.sendline(cmd)
	ssh_sess.prompt()
	if b"The command completed successfully" not in ssh_sess.before:
		print("Unmap drive output failed:", ssh_sess.before.decode())


def BackupFiles():
	""" Use robocopy to mirror the win_path to the share under the folder_name derived at the top.
	"""
	cmd = "robocopy \"{from_}\" \"{to}\" /ZB /MIR /COPY:DAT".format(from_=win_folder, to=backup_dst)

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
	samba.Start()
	print("Connecting SSH")
	ssh_sess = ConnectSSH()
	print("Mapping drive")
	MapNetworkDrive()
	print("Backing up files")
	BackupFiles()
	print("Unmapping drive")
	UnmapNetworkDrive()
	print("Disconnecting SSH")
	DisconnectSSH(ssh_sess)
	print("Stopping Samba")
	samba.Stop()


def main():
	DoBackup()


if __name__ == '__main__':
	main()