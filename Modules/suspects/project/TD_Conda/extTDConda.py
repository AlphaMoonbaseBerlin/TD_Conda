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
from functools import lru_cache

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
					0,
					self.libPathString
				)
				os.environ["_PYTHONPATH"] = os.environ.get("PYTHONPATH", "")
				os.environ["PYTHONPATH"] = self.libPathString

			def __exit__(mountSelf, type, value, traceback):
				del sys.path[0]
				os.environ["PYTHONPATH"] = os.environ["_PYTHONPATH"]
		self.Mount = Mount
	@property
	def condaEnv(self):
		Path( "TDImportCache/CondaTemp" ).mkdir(exist_ok=True, parents=True)
		Path( "TDImportCache/CondaHome" ).mkdir(exist_ok=True, parents=True)
		return {
			**os.environ,
			"PATH" : ";".join(
				os.environ["PATH"].split(";") + [
					str(self.condaDirectory.absolute()),
					str(Path(self.condaDirectory, "Scripts").absolute())
				]),
			"TEMP" 	: str(Path( "TDImportCache/CondaTemp" ).absolute()),
			"TMP" 	: str(Path( "TDImportCache/CondaTemp" ).absolute()),
			"USERPROFILE" 	: str(Path( "TDImportCache/CondaHome" ).absolute())
		}

	@property
	def libPathString(self):
		return str( Path(self.envDirectory, "Lib/site-packages").absolute() )

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
		debug( self.condaCommand(["shell.cmd.exe", "activate", self.envDirectory] ))
	
	@property
	def activationScript(self):
		return self._activationScript( self.envDirectory )
	
	@lru_cache
	def _activationScript(self, env):
		with open(self.condaCommand(["shell.cmd.exe", "activate", env])) as activationScript:
			return activationScript.read()
	

	def condaCommand(self, commands):
		return subprocess.check_output(
			[self.condaExe] + commands,
			env = self.condaEnv
		).decode()

	def envCommand(self, command):
		
		with subprocess.Popen(
			["cmd.exe"], 
			env=self.condaEnv,
			stdin=subprocess.PIPE ) as condaEnvContext:
			condaEnvContext.stdin.write( (self.activationScript + "\n").encode() )
			condaEnvContext.stdin.write( (" ".join([str(self.condaExe.absolute())] + command) + "\n").encode() )
			
			

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

	def Reset(self):
		self.condaCommand("config --remove-key proxy_servers".split(" "))
		self.condaCommand("clean --source-cache".split(" "))

	def Info(self):
		self.condaCommand(["info"])