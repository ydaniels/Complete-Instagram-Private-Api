import random
import csv
class UserAgent:

    parent=None

    def __init__(self,parent):

       self.parent = parent

    def getDeviceData(self):

        csvfile = __file__+'/devices.csv'

        line_of_text = [];
        reader_object = csv.reader(open(csvfile), delimiter=',', quotechar='"')
        for row in reader_object:
            line_of_text.append(row)

        deviceData =';'.join(line_of_text[random.randint(0, 11867)][0])
        
        return deviceData;

    def  buildUserAgent(self):
    
        deviceData = self.getDeviceData();
        self.parent.settings.set('manufacturer', deviceData[0]);
        self.parent.settings.set('device', deviceData[1]);
        self.parent.settings.set('model', deviceData[2]);
        return  'Instagram %s Android (18/4.3; 320dpi; 720x1280; %s; %s; %s; qcom; en_US)' % Constants.VERSION, deviceData[0], deviceData[1],deviceData[2]

