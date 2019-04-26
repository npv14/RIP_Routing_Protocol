import time
import socket
import sys
import select
import random
# import json
import pickle
import copy
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
    # print(outputs.keys())
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

global outPort
outPort = []

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
        table[int(i[2])] = [int(i[0]),int(i[1]), 0, 'True', 0]
        outPort.append(i[0])
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

def create_message(outputs):
    message = []
    version = "2"
    origin = routerId
    message.append(version)
    message.append(origin)
    message.append(outputs)
    data = pickle.dumps(message)
    return data

def send_data(portNo, outputs):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
    data = create_message(outputs)
    s.sendto(data,(HOST,portNo))

def receive(listSock, acceptedPort, original):
    global routerId, outputs
    # outputs = copy.deepcopy(original)
    Timeout = 1.0
    receive, _ , _ = select.select(listSock, [], [],Timeout)
    print("##############################################################")
    changed = False

    for sock in receive:
        changed = True
        data = sock.recvfrom(1024)  
        data = pickle.loads(data[0])
        data[2].pop(routerId)
        senderPort = original[data[1]][0]
        updateCost = [original[x][1] for x in original.keys() if x == data[1]].pop()
        
        print("Origin router: " + str(data[1]))
        print("Received routing table")
        print("senderPort:", senderPort)
        print("updateCost:", updateCost)
        
        # print("senderPort:", senderPort)
        for i in data[2].keys():

            print('data[1]', data[1])
            print('original.keys()', original.keys())
            print('data[1] in original.keys()', data[1] in original.keys())

            if data[1] in original.keys():
                print('original[data[1]][1]', original[data[1]][1])
                print('outputs[data[1]][1]', outputs[data[1]][1])
                print('original[data[1]][1] < outputs[data[1]][1]', original[data[1]][1] < outputs[data[1]][1])
                if original[data[1]][1] < outputs[data[1]][1]:
                    outputs[data[1]][0] = original[data[1]][0]
                    outputs[data[1]][1] = original[data[1]][1]
                    

            data[2][i][1] +=  updateCost
            if data[2][i][1] > 16:
                data[2][i][1] = 16
            
            if (i in outputs.keys() and data[2][i][3] == 'False' and outputs[i][0] == senderPort):
                outputs[i][1] = 16
                outputs[i][3] = 'False'

            if i not in outputs.keys():
                data[2][i][0] = senderPort
                outputs[i] =  data[2][i]

            else:
                if(outputs[i][1] > data[2][i][1]):
                    print('outputs[i][0] == senderPort) or (data[2][i][0] not in acceptedPort', (outputs[i][0] == senderPort) or (data[2][i][0] not in acceptedPort))
                    if (outputs[i][0] == senderPort) or (data[2][i][0] not in acceptedPort):
                        outputs[i][0] = senderPort
                        outputs[i][1] = data[2][i][1]   

            # if data[2][i][1] == 16:
                


        print("data[2]:", data[2])
        print("Outputs:", outputs)

        for key in outputs.keys():
            if key == data[1]:
                outputs[key][3] = 'True'
                outputs[key][2] = 0
                outputs[key][1] = original[key][1]


            if outputs[key][0] == senderPort and key != data[1]:
                outputs[key][3] = 'True'
                outputs[key][2] = 0
                # print('key', key)
                # print('data[2][key][1]', data[2][key][1])
                outputs[key][1] = data[2][key][1]

                # if (key in original.keys() and outputs[key][1] > original[key][1] and (senderPort == original[key][0]  or outputs[key][0] == original[key][0])):
                #     outputs[key][1] = original[key][1]

            # if outputs[key][2] > 30:
            #     outputs[key][1] = 16
                # outputs[key][3] = 'False'
        
        
                
                

        print('updateCost :',updateCost) 
    print("##############################################################")
    return changed, outputs


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
    global outputs, outPort
    try:
        fileName = sys.argv[1]
    except:
        print("ERROR: 404")

    then = time.time()
    invalidTime = time.time()
    routerId,acceptedPort,outputs = open_file(fileName)
    original = copy.deepcopy(outputs)
    print('acceptedPort:', acceptedPort)

    # Create sockets
    createdsocket = create_socket(acceptedPort) 
    # print(create_socket)

    timeUpdate = time.time()
    counter = 1
    while True:
        now = time.time() #Time after it finished
        
        if now-then > 4:
            

            for i in outputs.keys():
                outputs[i][2] += now - then
                

            recieved = receive(createdsocket, acceptedPort, original)
            
            for key in outputs.keys():
                if outputs[key][2] > 30:
                    outputs[key][1] = 16

                if outputs[key][2] > 40:
                    outputs[key][3] = 'False'

            if recieved:
                print('outputs:', outputs)
                print('original:', original)
                print_Routing_Table(routerId, outputs)


            for i in outPort:
                send_data(int(i), outputs)

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