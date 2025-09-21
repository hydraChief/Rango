import sys
from Interpreter import run
if __name__=="__main__":
    if (len(sys.argv)>=2):
        if sys.argv[1].split(".")[-1]=="rango":
            debugFlag=False
            if(len(sys.argv)>2):
                debugFlag=True
            run(sys.argv[1],debugFlag)
        else:
            print("FileExtension should be rango!!")
    else:
        print("Filename to interpreted not passed")