import time
import socket
import sys
import select
import random
# import json
import pickle

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
        table[int(i[2])] = [int(i[0]),int(i[1]), 0, 'True', 0]
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
    # print('##########################')
    # print(outputs)
    # print('##########################')
    message.append(version)
    message.append(origin)
    message.append(outputs)
    data = pickle.dumps(message)
    return data

def send_data(portNo, s):
    data = create_message()
    s.sendto(data,(HOST,portNo))

# def updateRoutingTable():



def receive(listSock):
    global routerId
    Timeout = 1.0
    receive, _ , _ = select.select(listSock, [], [],Timeout)
    print("##############################################################")
    for sock in receive:
        # print(sock)
        # print(sock.getsockname()[1])
        data = sock.recvfrom(1024)
        senderPort = data[1][1]
        data = pickle.loads(data[0])
        # add = pickle.loads(data[0])
        # print(data)
        # print("Version: " + data[0])
        # print("Origin router: " + str(data[1]))
        print("Received routing table")
        data[2].pop(routerId)
        print(data[2])
        cost = min([outputs[x][1] for x in outputs.keys() if outputs[x][0] == senderPort])
        print('cost :',cost)

        for i in data[2].keys():
            data[2][i][0] = senderPort
            if i not in outputs.keys():
                data[2][i][1] +=  cost
                outputs[i] =  data[2][i]

        print("Current routing table")
    print("##############################################################")
    # print(receive)

# def send(data, port=50000, addr='239.192.1.100'):
#     """send(data[, port[, addr]]) - multicasts a UDP datagram."""
#     # Create the socket
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # Make the socket multicast-aware, and set TTL.
#     s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20) # Change TTL (=20) to suit
#     # Send the data
#     s.sendto(data, (addr, port))

def print_Routing_Table(routerId, outputs): 
    print('Routing table for router:', routerId)
    header = ('{:^10}||'.format('Router-ID') + '{:^10}||'.format('PortNum') + '{:^10}||'.format('Metric') + '{:^15}||'.format('Invalid Timer') +
    '{:^11}||'.format('Reachable') + '{:^15}||'.format('flush Timer'))
    print(header)
    for i in sorted(outputs.keys()):
        line = '{:^10}||'.format(i) + '{:^10}||'.format(outputs[i][0]) + '{:^10}||'.format(outputs[i][1]) + '{:^15.3f}||'.format(outputs[i][2]) + '{:^11}||'.format(outputs[i][3]) +  '{:^15}||'.format(outputs[i][4])
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
            print_Routing_Table(routerId, outputs)
            #Some code for updating
            print("It took: ", now-then, " seconds")
            receive(createdsocket)
            # print(outputs)
            for i in outputs.keys():
                for socket in createdsocket:
                    # print(socket.getsockname()[1]%10)
                    if (socket.getsockname()[1]%10 == i):
                        send_data(outputs[i][0], socket)
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