import logging
import unittest
import re
from enum import Enum
import subprocess
from time import sleep


global logger


class ServiceStatus(Enum):
	Active = "active"
	Inactive = "inactive"
	Failed = "failed"
	Unknown = "unknown"


class Service:
	def __init__(self, name):
		self.name = name

	def Start():
		subprocess.call(["/usr/bin/systemctl", "start", self.SERVICE_NAME])

	def Stop():
		subprocess.call(["/usr/bin/systemctl", "stop", self.SERVICE_NAME])

	def Status():
		p = subprocess.Popen(["/usr/bin/systemctl", "status", self.SERVICE_NAME], stdout=subprocess.PIPE)
		stdout, _ = p.communicate()

		status = re.search(stdout, b"Active: ([\w]+)")
		if status is None:
			logger.warning("Couldn't find service status in systemctl status output")
			logger.debug("Status command output:", stdout)
			return ServiceStatus.unknown

		status = status.group(1)
		try:
			status = ServiceStatus(status)
		except ValueError:
			logger.warning("Unrecognized service status:", status)
			return ServiceStatus.Unknown

		return status


class Samba(Service):
	def __init__(self):
		super(Samba, self).__init__(self, "smb")


class TestService(unittest.TestCase):
	def setUpClass(cls):
		global logger
		try:
			logger
		except NameError:
			cls.create_logger()
		cls.service = Service("smb")


	def create_logger(self):
		global logger
		logger = logging.getLogger("Network_Share_Test")
		logger.setLevel(logging.WARNING)

		fh = logging.FileHandler("network_share_test.log")
		fh.setLevel(logging.DEBUG)

		ch = logging.StreamHandler()
		ch.setLevel(logging.WARNING)

		formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		logger.addHandler(fh)
		logger.addHandler(ch)


	def test_status(self):
		self.service.Start()
		sleep(1)
		status = self.service.Status()
		self.assertEquals(status, ServiceStatus.Active)

		self.service.Stop()
		sleep(1)
		status = self.service.Status()
		self.assertEquals(status, ServiceStatus.Inactive)



if __name__ == '__main__':
	unittest.main()