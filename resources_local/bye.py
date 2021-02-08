import os
import sys


def bye(scriptname):
    print('bye ' + scriptname)
    sys.exit()
    os.system('kill %', os.getpid())
    print('you never ever should see that !')
