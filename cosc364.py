import time
import socket
import sys
import select

def open_file(fileName):
    "Open the filename"
    f = open(fileName)
    infile = f.readlines()
    for i in infile:
        if "router-id" in i:
            routerId = i.split(' ')
            routerId = routerId[1]                              #Since router is always unique and only one
        if "input-port" in i:
            k = i.strip()
            inputPort = k.split(' ')
            inputPort = [i.strip(',') for i in inputPort[1:]]
            
        if "outputs" in i:
            l = i.strip()
            outputs = l.split(' ')
            outputs = [i.strip(',') for i in outputs[1:]]
    print(routerId)        
    print(outputs) 
    print(inputPort)


def main():
    try:
        fileName = sys.argv[1]
    except:
        print("ERROR: 404")
    openedFile = open_file(fileName)

if __name__ == "__main__":
    main()  