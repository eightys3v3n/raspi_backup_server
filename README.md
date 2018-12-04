# raspi_backup_server

Will run automatic backups of a Windows server over LAN using a Linux server to host a network share.

## Setup
### Windows
1. [Install OpenSSH on the Windows server](https://winscp.net/eng/docs/guide_windows_openssh_server#installing_sftp_ssh_server).
2. Configure the SSH server to port 443 or change the windows_ssh_port in main.py.
3. Change the Windows variables at the top of main.py accordingly.

### Linux
3. [Install Samba on the Linux server](https://wiki.archlinux.org/index.php/samba).
4. Add ports 137-139 and 445 to your firewall rules so the Samba share can be accessed.
4. Add a share on the Linux machine by putting the following in `/etc/samba/smb.conf`:
```
[share_name]
	comment = Some description
	browseable = yes
	writable = yes
	guest ok = no
	path = /the_path/to_your_backup/storing/folder
```
4. Modify the Linux variables at the top of main.py accordingly.
5. Put this script on the Linux machine and run it.