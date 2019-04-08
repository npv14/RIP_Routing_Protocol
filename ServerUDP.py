#SERVER PROGRAM


#Here we import for what is necessary for the server
import time
import socket
import sys
import select


MagicNo = 0x497E
PacketType = 0x0002


#This where the DT Request packet from the client is checked
def pkt_check(pkt):
    """Checks the recieved paket"""
    if len(pkt) != 6:
        print("ERROR: INVALID PACKET LENGTH")
        return False
    if int.from_bytes(pkt[0:2],byteorder='big') != 0x497E:
        print("ERROR: INVALID MAGICNO")
        return False
    if int.from_bytes(pkt[2:4],byteorder='big') != 0x001:
        print("ERROR: INVALID PAKCET TYPE")
        return False
    if int.from_bytes(pkt[4:6],byteorder='big') not in [0x0001,0x0002]:
        print("ERROR: INVALID REQUEST TYPE")
    return True

#This is where the server composes the packet neede to be sent to the client.
def DT_Response(MagicNo,PacketType,LanguageCode,pkt):
    """Composes the packet neede to send to the client"""
    array = bytearray()
    array = array + (int(MagicNo).to_bytes(2,byteorder='big'))
    array = array + (int(PacketType).to_bytes(2,byteorder='big'))
    array = array + (int(LanguageCode).to_bytes(2,byteorder='big'))
    array = array + (int(RequestDate()[0]).to_bytes(2,byteorder='big'))
    array = array + (int(RequestDate()[1]).to_bytes(1,byteorder='big'))
    array = array + (int(RequestDate()[2]).to_bytes(1,byteorder='big'))
    array = array + (int(RequestTime()[0]).to_bytes(1,byteorder='big'))
    array = array + (int(RequestTime()[1]).to_bytes(1,byteorder='big'))
    array = array + (int(13).to_bytes(1,byteorder='big'))
    if int.from_bytes(pkt[4:6],byteorder='big') == 0x0001:
        if LanguageCode == 0x0001:
            text_length = len(English()[0].encode('utf-8'))
            array = array + (text_length.to_bytes(1,byteorder='big'))
            array.extend(English()[0].encode('utf-8'))
        elif LanguageCode == 0x0002:
            text_length = len(Maori()[0].encode('utf-8'))
            array = array + (text_length.to_bytes(1,byteorder='big'))
            array.extend(Maori()[0].encode('utf-8'))
        else:
            text_length = len(German()[0].encode('utf-8'))
            array = array + (text_length.to_bytes(1,byteorder='big'))
            array.extend(German()[0].encode('utf-8'))
    else:
        if LanguageCode == 0x0001:
            array.extend(English()[1].encode('utf-8'))
        elif LanguageCode == 0x0002:
            array.extend(Maori()[1].encode('utf-8'))
        else:
            array.extend(German()[1].encode('utf-8'))
    return array


#The RequestDate() and RequestTime() function does the extracting from the time module
def RequestDate():
    """Creates date and time"""
    year = time.strftime('%Y')
    month = time.strftime('%m')
    day = time.strftime('%d')
    return year, month, day


def RequestTime():
    hour = time.strftime('%H')
    minute = time.strftime('%M')
    return hour, minute


#English(), German() and Maori() function creates a list of representing months which is later used for the sentece output. This function also creates a template sentence.
def English():
    """Contains the English month used for the representation"""
    index = int(RequestDate()[1])
    monthlist = ['January','February','March','April','May','June','July','August','September','October','November','December']
    date = "Today's date is {} {}, {}".format(RequestDate()[2],monthlist[index],RequestDate()[0])
    time = "The current time is {}:{}".format(RequestTime()[0],RequestTime()[1])
    return date, time


def Maori():
    """Contains the Maori month used for the representation"""
    index = int(RequestDate()[1])
    monthlist = ['KohitaŻtea','Hui-tanguru','PoutuŻ-te-rangi','Paenga-whŻawhŻa','Haratua','Pipiri','HoŻngongoi','Here-turi-kŻokaŻ','Mahuru','Whiringa-aŻ-nuku','Whiringa-aŻ-rangi','Hakihea']
    date = "Ko te ra o tenei ra ko {} {}, {}".format(RequestDate()[2],monthlist[index],RequestDate()[0])
    time = "Ko te wa o tenei wa {}:{}".format(RequestTime()[0],RequestTime()[1])
    return date, time


def German():
    """Contains the German month used for the representation"""
    index = int(RequestDate()[1])
    monthlist = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']
    date = "Heute ist der {} {}, {}".format(RequestDate()[2],monthlist[index],RequestDate()[0])
    time = "Die Uhrzeit ist {}:{}".format(RequestTime()[0],RequestTime()[1])
    return date,time


def check_port(EnglishPort,GermanPort,MaoriPort):
    """Checks the port whether it is in range 1024 and 64000 or not"""
    port = [EnglishPort,GermanPort,MaoriPort]
    flag = True
    for i in port:
        if i not in range(1024,64000):
            flag = flag & False
    return flag


def main():
    """This is the main function where it does the sending and receiveing"""
    try :
        EnglishPort = int(sys.argv[1])
        MaoriPort = int(sys.argv[2])
        GermanPort = int(sys.argv[3])
    except:
        print("ERROR: PORT NUMBER MUST BE AN INTEGER")
        exit()

    if EnglishPort == GermanPort or EnglishPort == MaoriPort or GermanPort == MaoriPort:
        print('ERROR: PORT NUMBER SHOULD NOT BE THE SAME')
        exit()
    if check_port(EnglishPort,GermanPort,MaoriPort) == False:
        print("ERROR: PORT NUMBER MUST BE IN RANGE 1024 AND 64000")
        exit()
    #Creates the socket for each language and for sending
    EnglishSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MaoriSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    GermanSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Sending = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    #Tries to bind the socket and if it fails it closes
    try:
        EnglishSocket.bind((host, EnglishPort))
        GermanSocket.bind((host, GermanPort))
        MaoriSocket.bind((host, MaoriPort))
    except:
        print("ERROR: PORT ERROR")
        EnglishSocket.close()
        GermanSocket.close()
        MaoriSocket.close()
    #This is where the infinite looping begins
    while True:
        sockets = [EnglishSocket,MaoriSocket,GermanSocket]
        receive, _ , _ = select.select(sockets, [], [])
        for i in receive:
            if i in sockets:
                data, address = i.recvfrom(1024)
                #Checks the packet, go back to the top of the loop if wrong packet
                if pkt_check(data) is False:
                    break
                #Checks which socket was used to determine the language code
                if i == EnglishSocket:
                    LanguageCode = 0x0001
                elif i == MaoriSocket:
                    LanguageCode = 0x0002
                else:
                    LanguageCode = 0x0003
                #Sends the packet
                MESSAGE = DT_Response(MagicNo,PacketType,LanguageCode,data)
                Sending.sendto(MESSAGE, address)
            else:
                print('ERROR: FAILED TO CONNECT TO PORT')
    


if __name__ == "__main__":
    main()
