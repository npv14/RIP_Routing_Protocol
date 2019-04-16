#CLIENT PROGRAM


#Here we import for what is necessary for the Client
import socket
import sys
import select

MagicNo = 0x497E
PacketType = 0x0001
MinPort = 1024
MaxPort = 64000


def DT_Request(MagicNo, PacketType, RequestType):
    """Compose packet to be sent to the server"""
    array = bytearray()
    array = array + (int(MagicNo).to_bytes(2,byteorder='big'))
    array = array + (int(PacketType).to_bytes(2,byteorder='big'))
    array = array + (int(RequestType).to_bytes(2,byteorder='big'))
    return array


#For each if statement there's a return because no point continuing if its invalid
def pkt_check(pkt):
    """Checks the received packet from the server whether it is valid or not"""
    if len(pkt) < 13:
        print("ERROR: INVALID PACKET LENGTH")
        return False
    if int.from_bytes(pkt[0:2],byteorder='big') != 0x497E:
        print("ERROR: INVALID MAGICNO")
        return False
    if int.from_bytes(pkt[2:4],byteorder='big') != 0x0002:
        print("ERROR: INVALID PACKET TYPE")
        return False
    if int.from_bytes(pkt[4:6],byteorder='big') not in  [0x0001,0x0002,0x0003]:
        print("ERROR: INVALID LANGUAGE CODE")
        return False
    if int.from_bytes(pkt[6:8],byteorder='big') > 2100:
        print("ERROR: INVALID YEAR")
        return False
    if int.from_bytes(pkt[8:9],byteorder='big') not in range(1,12):
        print("ERROR: INVALID MONTH")
        return False
    if int.from_bytes(pkt[9:10],byteorder='big') not in range(1,31):
        print("ERROR: INVALID DAY")
        return False
    if int.from_bytes(pkt[10:11],byteorder='big') not in range(0,23):
        print("ERROR: INVALID HOUR")
        return False
    if int.from_bytes(pkt[11:12],byteorder='big') not in range(0,59):
        print("ERROR: INVALID MINUTE")
        return False
    if len(pkt) != 13 + len(pkt[13:]):
        print("ERROR: INVALID LENGTH")
        return False
    print("MagicNo:",hex(int.from_bytes(pkt[0:2],byteorder='big')))
    print("Packet Type:","0x%0.4X" % int.from_bytes(pkt[2:4],byteorder='big'))
    print("Language Code:","0x%0.4X" % int.from_bytes(pkt[4:6],byteorder='big'))
    print("Year:",int.from_bytes(pkt[6:8],byteorder='big'))
    print("Month:",int.from_bytes(pkt[8:9],byteorder='big'))
    print("Day:",int.from_bytes(pkt[9:10],byteorder='big'))
    print("Hour:",int.from_bytes(pkt[10:11],byteorder='big'))
    print("Minute:",int.from_bytes(pkt[11:12],byteorder='big'))
    print("Length:",int.from_bytes(pkt[12:13],byteorder='big'))
    return True


def IPCheck(address):
    """Checks the validity of the IP address"""
    try:
        socket.inet_pton(socket.AF_INET, address)
        return True
    except socket.error:
        try:
            socket.inet_aton(address)
        except:
            return False
        return address.count('.') == 3
    except socket.error:
        return False


def main():
    """This is the main function where it does the sending and receiveing"""
    try:
        RequestType = sys.argv[1]
        RequestIP = sys.argv[2]
        RequestPort = int(sys.argv[3])
    except:
        pass

    if RequestType == 'date':
        RequestType = 0x0001
        MESSAGE = DT_Request(MagicNo, PacketType, RequestType)
    elif RequestType == 'time':
        RequestType = 0x0002
        MESSAGE = DT_Request(MagicNo, PacketType, RequestType)
    else:
        print("ERROR: YOU HAVE ENTERED AN UNKNOWN REQUEST")
        exit()

    if RequestPort not in range(MinPort, MaxPort):
        print("ERROR: PORT NUMBER MUST BE IN RANGE 1024 AND 64000")
        exit()
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = socket.getaddrinfo(RequestIP,RequestPort)
        IPaddress = socket.gethostbyname(RequestIP)
        if RequestIP == str(address[0][4][0]) or RequestIP == IPaddress:
            sock.sendto(MESSAGE, (RequestIP, RequestPort))
        else:
            print("ERROR: INVALID IP ADDRESS")
            sock.close()
            exit()

    while True:
        Timeout = 1.0
        receive, _ , _ = select.select([sock], [], [],Timeout)
        if receive:
            data, address = sock.recvfrom(1024)
            if pkt_check(data) is False:
                sock.close()
                exit()

            print(data[13:].decode('utf-8'))
            sock.close()
            exit()
        else:
            print("ERROR: SESSION TIMED OUT")
            return
if __name__ == "__main__":
    main()
