import time
from time import localtime, gmtime, strftime

t = int(strftime("%H", localtime()))
print(t)
t = int(strftime("%H", gmtime()))
print(t)

