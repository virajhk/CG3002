import serial
import time
ser = serial.Serial('/dev/ttyAMA0',9600,timeout=1)

first_ack = 0
handshake = 1
keypad = 1
start_building = 100
end_building = 100
start_level = 100
end_level = 100
start_node = 100
end_node = 100
start = ''
end = ''
heading = 0
steps = 0
alti = 0
millis_prev_acc = int (round(time.time() * 1000))
millis_prev_ultra = int (round(time.time() * 1000))
millis_prev_mag = int (round(time.time() * 1000))
millis_prev_ir = int (round(time.time() * 1000))
millis_prev_alti = int (round(time.time() * 1000))

try:
        while handshake:
                if (first_ack == 0):
                        ser.write("h")
                response = ser.readline()
                if (response != ''):
                        print response
                if (first_ack == 1):
                        ser.write("a")
                        handshake = 0
                        print "Handshake established"
                if (first_ack == 0 and response == "a"):
                        first_ack = 1

        while keypad:
                ser.write("z")
                response = ser.readline()
                #print response
                if (response != '' and start_building == 100):
                        start_building = response.split('.')
                        print int(start_building[0])/10
                elif (response != '' and start_level == 100):
                        start_level = response.split('.')
                        print int(start_level[0])/10
                elif (response != '' and start_node == 100):
                        start_node = response.split('.')
                        print int(start_node[0])/10
                elif (response != '' and end_building == 100):
                        end_building = response.split('.')
                        print int(end_building[0])/10
                elif (response != '' and end_level == 100):
                        end_level = response.split('.')
                        print int(end_level[0])/10
                elif (response != '' and end_node == 100):
                        end_node = response.split('.')
                        print int(end_node[0])/10
                elif (start_building != 100 and start_level != 100 and start_node != 100 and end_building != 100 and end_level != 100 and end_node != 100):
                        keypad = 0;
                        start = str(start_building) + str(start_level) + str(start_node)
                        end = str(end_building) + str(end_level) + str(end_node)

        while 1:
                millis_current_alti = int (round(time.time() * 1000))
                if ((millis_current_alti - millis_prev_alti) > 100000):
                        ser.write("5")
                        response = ser.readline()
                        #print response
                        if (response != ''):
                                res = response.split(",")
                                #print res
                                alti = int(res[0])
                                print "Alti:"
                                print alti
                        millis_prev_alti = millis_current_alti

                millis_current_ir = int (round(time.time() * 1000))
                if ((millis_current_ir - millis_prev_ir) > 500):
                        ser.write("6")
                        response = ser.readline()
                        #print response
                        if (response != ''):
                                res = response.split(",")
                                #print res
                                ir = res[0]
                                print "Infrared Sensor:"
                                print ir
                        millis_prev_ir = millis_current_ir

                millis_current_acc = int (round(time.time() * 1000))
                if ((millis_current_acc - millis_prev_acc) > 500):
                        ser.write("7")
                        response = ser.readline()
                        #print response
                        if (response != ''):
                                res = response.split(",")
                                #print res
                                #accX = res[0]
                                #accY = res[1]
                                #accZ = res[2]
                                steps = int(res[0])
                                print "Accelerometer (Steps):"
                                #print accX
                                #print accY
                                #print accZ
                                print steps
                        millis_prev_acc = millis_current_acc

                millis_current_mag = int (round(time.time() * 1000))
                if ((millis_current_mag - millis_prev_mag) > 500):
                        ser.write("8")
                        response = ser.readline()
                        #print response
                        if (response != ''):
                                res = response.split(",")
                                #print res
                                #magX = res[0]
                                #magY = res[1]
                                #magZ = res[2]
                                heading = int(res[0])
                                print "Magnetometer (Heading in degrees):"
                                #print magX
                                #print magY
                                #print magZ
                                print heading
                        millis_prev_mag = millis_current_mag
                                #accZ = res[2]

                millis_current_ultra = int (round(time.time() * 1000))
                if ((millis_current_ultra - millis_prev_ultra) > 500):
                        #ser.write("9")

                        millis_prev_ultra = millis_current_ultra
                        
except KeyboardInterrupt:
        ser.close()

