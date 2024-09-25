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
		return Path(self.condaDirectory, "_conda.exe")
	
	def Setup(self):
		if not self.condaDirectory.is_dir(): self.downloadAndUnpack()
		if not self.envDirectory.is_dir(): self.createEnv()
		
	def condaCommand(self, commands):
		subprocess.call(
			[self.condaExe] + commands
		)

	def envCommand(self, command):
		"""
		export PATH='/Users/username/.local/anaconda/envs/mamba-poc/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/username/.local/anaconda/condabin:/opt/homebrew/bin:/opt/homebrew/sbin'
		export CONDA_PREFIX='/Users/username/.local/anaconda/envs/mamba-poc'
		export CONDA_SHLVL='2'
		export CONDA_DEFAULT_ENV='mamba-poc'
		export CONDA_PROMPT_MODIFIER='(mamba-poc) '
		export CONDA_EXE='/Users/username/.local/anaconda/bin/conda'
		export _CE_M=''
		export _CE_CONDA=''
		export CONDA_PYTHON_EXE='/Users/username/.local/anaconda/bin/python'
		export CONDA_PREFIX_1='/Users/username/.local/anaconda'"""
		condaEnv = {
			"PATH" : os.environ["path"] + ";" + str(self.condaDirectory.absolute()),
			"CONDA_PREFIX" : str(self.envDirectory.absolute()),
			"CONDA_SHLVL" : "2",
			"CONDA_DEFAULT_ENV" : str(self.envDirectory.absolute()),
			"CONDA_PROMPT_MODIFIER" : self.ownerComp.par.Envname.eval(),
			"CONDA_EXE" : str(self.condaDirectory.absolute()),
			"_CE_M" : "",
			"_CE_CONDA" : "",
			"CONDA_PYTHON_EXE" : str( self.condaDirectory.absolute() ),
			"CONDA_PREFIX_1" : str( self.envFolder.absolute())
		}

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
				f'/D={self.condaDirectory.absolute()}'
			])
			# result = installProcess.wait()
		#
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
	