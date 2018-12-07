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

	def Start(self):
		p = subprocess.run(["system/usr/bin/systemctl", "start", self.name])

	def Stop(self):
		p = subprocess.run(["/usr/bin/systemctl", "stop", self.name])

	def Status(self):
		p = subprocess.Popen(["/usr/bin/systemctl", "status", self.name], stdout=subprocess.PIPE)
		stdout, _ = p.communicate()

		logger.info("Getting status of service '{}'".format(self.name))
		status = re.search(b"Active: ([\w]+) ", stdout)

		if status is None:
			logger.warning("Couldn't find service status in systemctl output")
			logger.debug("Status command output: {}".format(stdout))
			return ServiceStatus.Unknown

		status = status.group(1).decode()
		try:
			status = ServiceStatus(status)
		except ValueError:
			logger.warning("Unrecognized service status: {}".format(status))
			return ServiceStatus.Unknown

		return status


class Samba(Service):
	def __init__(self):
		super(Samba, self).__init__(self, "smb")


class TestService(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		global logger
		try:
			logger
		except NameError:
			cls.create_logger(cls)
		cls.service = Service("smb")


	@classmethod
	def tearDownClass(cls):
		logging.shutdown()


	def create_logger(self):
		global logger
		logger = logging.getLogger("Network_Share_Test")
		logger.setLevel(logging.WARNING)

		# fh = logging.FileHandler("network_share_test.log")
		# fh.setLevel(logging.DEBUG)

		ch = logging.StreamHandler()
		ch.setLevel(logging.INFO)

		formatter = logging.Formatter("%(asctime)s %(name)s (%(levelname)s): %(message)s")
		# fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		# logger.addHandler(fh)
		logger.addHandler(ch)


	def test_status(self):
		status = self.service.Status()
		cmd = "systemctl status {} | sed -rn 's/\\s+Active:\\s+([a-z]+)\\s+.*/\\1/p'".format(self.service.name)
		p = subprocess.run(cmd, shell=True, capture_output=True)
		parsed_status = p.stdout[0:-1]
		parsed_status = parsed_status.decode()
		self.assertNotEqual(parsed_status, "")
		self.assertEqual(parsed_status, status.value)


	def test_start(self):
		self.service.Start()
		status = self.service.Status()
		self.assertEqual(status, ServiceStatus.Active)


	def test_stop(self):
		self.service.Stop()
		status = self.service.Status()
		self.assertEqual(status, ServiceStatus.Inactive)


if __name__ == '__main__':
	unittest.main()