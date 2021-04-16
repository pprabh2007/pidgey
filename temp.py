import os

files = os.listdir()
print(files)

for file in files:
	if file.endswith(".py"):
		print(file)