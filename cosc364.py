import time
import socket
import sys
import select
import random
import json

HOST = '127.0.0.1'
global routerId, outputs

def open_file(fileName):
    "Open the filename"
    global routerId, outputs
    table = {}
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

    # print(routerId)
    # print(acceptedPort)        
    print(outputs.keys())
    print("List of rejected ports : {}".format(rejectedPort))
    return (routerId,acceptedPort,outputs)

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
    table = {}
    for i in outputs:
        i = i.split('-')
        if int(i[0]) < 1024 and int(i[0]) > 64000:
            return "Invalid port range"
        if int(i[0]) in acceptedPort:
            print("Port same as input port")
            return "Port same as input port"
        list = [int(i[0]),int(i[1]),int(i[2])]
        table[int(i[2])] = [int(i[0]),int(i[1]), 0, 0]
    return table

def create_socket(acceptedPort):
    "Creates the socket"
    sockets = []
    try: 
        for i in acceptedPort:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(("0.0.0.0", i))
            sockets.append(s)
            # print(sockets)
        return sockets
    except socket.error as err: 
            print("socket creation failed with error %s" %(err))

def create_message():
    message = []
    version = "2"
    origin = routerId
    message.append(version)
    message.append(origin)
    message.append(outputs)
    data = json.dumps({"a":message})
    return data

def send_data(portNo):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = create_message()
    s.sendto(data.encode(),(HOST,portNo))

def receive(listSock):
    Timeout = 1.0
    receive, _ , _ = select.select(listSock, [], [],Timeout)
    print("##############################################################")
    print(receive)

# def send(data, port=50000, addr='239.192.1.100'):
#     """send(data[, port[, addr]]) - multicasts a UDP datagram."""
#     # Create the socket
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # Make the socket multicast-aware, and set TTL.
#     s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20) # Change TTL (=20) to suit
#     # Send the data
#     s.sendto(data, (addr, port))

def print_Routing_Table():
    global routerId, outputs
    print('Routing table for router:', routerId)
    header = '{:^10}||'.format('Router-ID') + '{:^10}||'.format('PortNum') + '{:^10}||'.format('Metric') + '{:^15}||'.format('Invalid Timer') + '{:^15}||'.format('flush Timer')
    print(header)
    for i in outputs.keys():
        line = '{:^10}||'.format(i) + '{:^10}||'.format(outputs[i][0]) + '{:^10}||'.format(outputs[i][1]) + '{:^15.3f}||'.format(outputs[i][2]) + '{:^15}||'.format(outputs[i][3])
        print(line)
    

def main():
    global outputs
    try:
        fileName = sys.argv[1]
    except:
        print("ERROR: 404")
    then = time.time()
    invalidTime = time.time()
    routerId,acceptedPort,outputs = open_file(fileName)
    createdsocket = create_socket(acceptedPort)
    # print(create_socket)
    counter = 1
    while True:
        
        now = time.time() #Time after it finished
        
        if now-then > 4:
            # create_message()
            for i in outputs.keys():
                outputs[i][2] = now - invalidTime
            print_Routing_Table()
            #Some code for updating
            print("It took: ", now-then, " seconds")
            receive(createdsocket)
            for i in outputs.keys():
                send_data(outputs[i][0])
            then = now
            continue

        
        
        # print("Loop " + str(counter))
        # maxtime = 10 + random.randint(-3,3)
        # timeout = maxtime
        # track = time.time()
        # elapsed = track - time.time()
        # timer_incr = 0
        # print(maxtime)
        # print(elapsed)
        

if __name__ == "__main__":
    main()  