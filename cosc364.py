import time
import socket
import sys
import select

def open_file(fileName):
    "Open the filename"
    flag1 = False
    flag2 = False
    flag3 = False
    f = open(fileName)
    infile = f.readlines()
    for i in infile:
        if "router-id" in i:
            routerId = i.split(' ')
            routerId = routerId[1]                              #Since router is always unique and only one
            routerId = check_router_id(routerId)
            flag1 = True
        if "input-port" in i:
            k = i.strip()
            inputPort = k.split(' ')
            inputPort = [i.strip(',') for i in inputPort[1:]]
            flag2 = True           
        if "outputs" in i:
            l = i.strip()
            outputs = l.split(' ')
            outputs = [i.strip(',') for i in outputs[1:]]
            flag3 = True
    if (flag1 and flag2 and flag3 is False):
        print("Error in config file")
        return
    acceptedPort,rejectedPort = check_inputPort(inputPort)
    outputs = check_outputs(outputs,acceptedPort)                    
    print(routerId)
    print(acceptedPort)        
    print(rejectedPort)
    print(outputs)
    return (routerId,inputPort,outputs)

def check_router_id(routerId):
    "Sanity check for the router ID"
    if int(routerId) >= 1 and int(routerId) <= 64000:
        return int(routerId)
    else:
        return "Invalid router Id"

def check_inputPort(inputPort):
    "Sanity check for the input port"
    acceptedPort = []
    rejectedPort = []
    inputPort = set(inputPort)
    for i in inputPort:
        try:
            i = int(i)
            if i >= 1024 and i <= 64000:
                acceptedPort.append(i)
            else:
                rejectedPort.append(i)
        except:
            print("port number is a string")
            rejectedPort.append(i)
    return(acceptedPort,rejectedPort)

def check_outputs(outputs,acceptedPort):
    "Sanity check for the output"
    outputPort = []
    for i in outputs:
        i = i.split('-')
        if int(i[0]) < 1024 and int(i[0]) > 64000:
            return "Invalid port range"
        if int(i[0]) in acceptedPort:
            print("Port same as input port")
            return "Port same as input port"
        list = [int(i[0]),int(i[1]),int(i[2])]
        outputPort.append(list)
    return outputPort

def main():
    try:
        fileName = sys.argv[1]
    except:
        print("ERROR: 404")
    openedFile = open_file(fileName)

if __name__ == "__main__":
    main()  