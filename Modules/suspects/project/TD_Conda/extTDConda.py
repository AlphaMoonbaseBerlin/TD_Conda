'''Info Header Start
Name : extTDConda
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2023.11880
Info Header End'''



from pathlib import Path
import subprocess
from platform import python_version
import sys
import os

class extTDConda:
	"""
	extTDConda description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.log = self.ownerComp.op("logger").Log
		class Mount(object):
			def __init__(mountSelf):
				pass
			def __enter__(mountSelf):
				sys.path.insert(
					Path( self.envDirectory, "lib"),
					0
				)
				os.environ["_PYTHONPATH"] = os.environ["PYTHONPATH"]
				os.environ["PYTHONPATH"] = Path( self.envDirectory, "lib")
			def __exit__(mountSelf, type, value, traceback):
				del sys.path[0]
				os.environ["PYTHONPATH"] = os.environ["_PYTHONPATH"]
	
	@property
	def condaEnv(self):
		Path( "TDImportCache/CondaTemp" ).mkdir(exist_ok=True, parents=True)
		Path( "TDImportCache/CondaHome" ).mkdir(exist_ok=True, parents=True)
		return {
			"PATH" : ";".join(
				os.environ["PATH"].split(";") + [
					str(self.condaDirectory.absolute()),
					str(Path(self.condaDirectory, "Scripts").absolute())
				]),
			"TEMP" : str(Path( "TDImportCache/CondaTemp" ).absolute()),
			"TMP" : str(Path( "TDImportCache/CondaTemp" ).absolute()),
			"HOME" : str(Path( "TDImportCache/CondaHome" ).absolute())
			
		}

	@property
	def condaDirectory(self):
		return Path(self.ownerComp.par.Condafolder.eval())

	@property
	def envFolder(self):
		return Path(self.ownerComp.par.Envfolder.eval())

	@property
	def envDirectory(self):
		return Path(self.envFolder, self.ownerComp.par.Envname.eval())
	
	@property
	def condaExe(self):
		return Path(self.condaDirectory, "conda.exe")
	
	def Setup(self):
		if not self.condaDirectory.is_dir(): self.downloadAndUnpack()
		if not self.envDirectory.is_dir(): self.createEnv()
		
	def condaCommand(self, commands):
		subprocess.call(
			[self.condaExe] + commands,
			env = self.condaEnv
		)

	def envCommand(self, command):
		subprocess.call(
			["conda", "activate", self.envDirectory.absolute()], 
			env={
				"PATH" : str(Path(self.condaDirectory, "condabin").absolute())
			})

		subprocess.call([self.condaExe] + command, env=condaEnv)

	def Install(self, package):
		self.envCommand(["install", package])
	

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
				"/NoRegistry=1", 
				"/NoScripts=1", 
				"/NoShortcuts=1",
				f'/D={self.condaDirectory.absolute()}'
			])
			# result = installProcess.wait()
		#	
		except subprocess.CalledProcessError as grepexc:                                                                                                   
			self.log("error code", grepexc.returncode, grepexc.output)
		self.log("Installed Conda")
		os.rename(
			Path(self.condaDirectory, "_conda.exe"),
			Path(self.condaDirectory, "conda.exe")
		)
		self.log("Renamed _conda.exe")

	def createEnv(self):
		# self.envDirectory.mkdir(exist_ok=True, parents=True)
		self.log("Trying to create the environment.")
		self.condaCommand([
			"create", "-y",
			"--no-shortcuts",
			"-k",
			"-p", f'{self.envDirectory.absolute()}',
			f"python={'.'.join(python_version().split('.')[0:2])}"
			
			# Afaik Conda is not supporting the current version. Lol.
		])
		self.log("Created the env I hope.")
		# We might need to run conda init after install. This will have an impact on the os so
		# It would be nice to find a way of using conda without having to change the 
		# Target OS