'''Info Header Start
Name : extTDConda
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2023.11880
Info Header End'''



from pathlib import Path
import subprocess
from platform import python_version

class extTDConda:
	"""
	extTDConda description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.log = self.ownerComp.op("logger").Log

	@property
	def condaDirectory(self):
		return Path("TDImportCache/Conda")

	@property
	def envDirectory(self):
		return Path("_condaEnv")

	def Setup(self):
		if not self.condaDirectory.is_dir(): self.downloadAndUnpack()
		if not self.envDirectory.is_dir(): self.createEnv()
		
	def condaCommand(self, commands):
		subprocess.call(
			[Path(self.condaDirectory, "_conda.exe")] + commands
		)

	def downloadAndUnpack(self):
		# Downlading 
		self.log("Downloadin COnda Installer")
		condaInstaller:Path 				= self.ownerComp.op("condaDependency").GetRemoteFilepath()
		self.log("RUnning Installer")
		#self.condaDirectory.mkdir(exist_ok=True, parents=True)

		try:
			result = subprocess.call([
				condaInstaller,
				"/S", 
				"/InstallationType=JustMe",
				"/AddToPath=0",
				"/RegisterPython=0",
				f'/D={self.condaDirectory.absolute()}'
			])
			# result = installProcess.wait()
			self.log("Cannot reach? Whut?")
			self.log("Run installer, result", result)
		except subprocess.CalledProcessError as grepexc:                                                                                                   
			self.log("error code", grepexc.returncode, grepexc.output)

	def createEnv(self):
		# self.envDirectory.mkdir(exist_ok=True, parents=True)

		self.condaCommand([
			"create", "-y","-p", 
			f'{self.envDirectory.absolute()}',
			f"python={'.'.join(python_version().split('.')[0:2])}"
			
			# Afaik Conda is not supporting the current version. Lol.
		])
	