import shutil, glob, fileinput, sys, os

# Variables
itemsCopied = 0
run = 0

# Generic copying validation by number of files to copy
def checkCopy(itemsToCopy):
	global itemsCopied
	if itemsCopied != itemsToCopy:
		sys.exit("Invalid number of copied items! Copied " + str(itemsCopied) + " Should be " + str(itemsToCopy))
	itemsCopied = 0

# Copy files by full name
def copyFilesByName(source, target):
	global itemsCopied, run
	if not os.path.isfile(source):
		sys.exit("File not exists: " + source)
	print("Copying " + source + " to " + target)
	itemsCopied+=1
	if run:
		shutil.copy(source, target)


# Copy files by globbing
def copyFilesByGlob(source, target):
	global itemsCopied, run
	for file in glob.glob(source):
	    print("Copying globbed " + file + " to " + target)
	    itemsCopied+=1
	    if run:
	    	shutil.copy(file, target)

# Copy entire tree (folder)
def copyTree(source, target):
	global itemsCopied, run
	print("Copying tree " + source + " to " + target)
	itemsCopied+=1
	if run:
		shutil.rmtree(target)
		shutil.copytree(source, target)

# Replace "replacewhat" in fileToEdit with "replaceWith"
def replaceInFile(fileToEdit, replaceWhat, replaceWith):
	global run
	if run:
		with fileinput.FileInput(fileToEdit, inplace=True) as file:
			for line in file:
				print(line.replace(replaceWhat, replaceWith), end='')

# Replace "replacewhat" in globbed filesToEdit with "replaceWith"
def replaceInFileByGlob(filesToEdit, replaceWhat, replaceWith):
	global run
	for globbedFile in glob.glob(filesToEdit):
		print("Editing globbed file " + globbedFile)
		with fileinput.FileInput(globbedFile, inplace=True) as file:
			for line in file:
				if run:
					print(line.replace(replaceWhat, replaceWith), end='')