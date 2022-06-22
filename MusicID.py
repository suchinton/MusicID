import os
from tokenize import String

directories = os.system("ls -lh")
print(directories)

# You could also use the os.popen() method
Lol = os.system("echo $(neofetch) | grep os")
print (Lol)

print ("hello")