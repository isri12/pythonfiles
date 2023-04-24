import time
from time import strftime, localtime


def epoch():
    ticks = time.time()
    # print ("Number of ticks since 12:00am, January 1, 1970(Epoch):", ticks)
    # time.sleep(1)   #sleep 1 sec 
    return ticks


# Convert epoch to human-readable date

def fromEpochToUnix():
    AscTime=time.asctime()
    return AscTime


def fromEpochToUnixNum():
    AscTime2=strftime('%Y-%m-%d %H:%M:%S', localtime(int(epoch())))
    return AscTime2


def stopwatch():
    inputSeconds=int(input("Enter stopwatch in second: "))
    i=0
    while i<inputSeconds:
        i+=1
        time.sleep(1)
        print(i)

def main():
    print(epoch())
    print(fromEpochToUnix())
    print(fromEpochToUnixNum())
    stopwatch()


main()