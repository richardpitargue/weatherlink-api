import struct

class DataParser():

    def __init__(self):
        self.directions = [
            'N',
            'NNE',
            'NE',
            'ENE',
            'E',
            'ESE',
            'SE',
            'SSE',
            'S',
            'SSW',
            'SW',
            'WSW',
            'W',
            'WNW',
            'NW',
            'NNW'
        ]

    def testDash(self, value, dashValue):
        if value == dashValue:
            return -1
        else:
            return value

    def testDashDivide(self, value, dashValue, dividend):
        res = self.testDash(value, dashValue)
        if res == -1:
            return -1
        else:
            return (res/dividend)

    def testDashConvertToC(self, value, dashValue, dividend):
        res = self.testDash(value, dashValue)
        if res == -1:
            return -1
        else:
            return float("%.2f" % (((res/dividend) - 32) / 1.8))

    def testDashAdd(self, value, dashValue, addend):
        res = self.testDash(value, dashValue)
        if res == -1:
            return -1
        else:
            return (res+addend)

    def testDashAddConvertToC(self, value, dashValue, addend):
        res = self.testDash(value, dashValue)
        if res == -1:
            return -1
        else:
            return float("%.2f" % (((res + addend) - 32) / 1.8))

    def parse(self, file_name, station_id):
        data = []
        prev_year = None

        with open(file_name, 'rb') as file:
            bin = file.read(52)
            while bin:
                u = struct.unpack('HHHHHHHHHHHBBBBBBBBHBBBBBBBBBBBBBBBBBBBB', bin)

                cur_year = (u[0] >> 9) + 2000
                if prev_year is None:
                    prev_year = cur_year
                elif (prev_year != cur_year) and (prev_year != (cur_year+1)):
                    bin = file.read(52)
                    continue

                data.append({
                    'stationId': station_id,
                    'date': {
                        'year': (u[0] >> 9) + 2000,
                        'month': (u[0] >> 5) & 0x000F,
                        'day': u[0] & 0x001F
                    },
                    'time': {
                        'hour': int(u[1]/100),
                        'minute': u[1]-(int(u[1]/100))*100
                    },
                    'data': {
                        'temp': {
                            'ave': self.testDashConvertToC(u[2], 32767, 10),
                            'min': self.testDashConvertToC(u[2], -32768, 10),
                            'max': self.testDashConvertToC(u[2], 32767, 10),
                            'inside': self.testDashConvertToC(u[10], 32767, 10)
                        },
                        'rainfall': u[5],
                        'maxRainfall': u[6],
                        'barometer': u[7]/1000,
                        'solarRadiation': {
                            'ave': self.testDash(u[8], 32767),
                            'max': u[19]
                        },
                        'windSample': u[9],
                        'humidity': {
                            'inside': self.testDash(u[11], 255),
                            'outside': self.testDash(u[12], 255)
                        },
                        'wind': {
                            'ave': self.testDash(u[13], 255),
                            'max': u[14],
                            'direction': {
                                'max': self.directions[u[15]] if u[15] != 255 else 'None',
                                'prevailing': self.directions[u[16]] if u[16] != 255 else 'None'
                            }
                        },
                        'UV': {
                            'ave': self.testDashDivide(u[17], 255, 10),
                            'max': u[20]/10
                        },
                        'ET': u[18]/1000,
                        'forecastRule': self.testDash(u[21], 193),
                        'leaf': {
                            'temp': [self.testDashAddConvertToC(u[22], 255, 90), self.testDashAddConvertToC(u[23], 255, 90)],
                            'wetness': [self.testDash(u[24], 255), self.testDash(u[25], 255)]
                        },
                        'soil': {
                            'temp': [self.testDashAddConvertToC(u[26], 255, 90), self.testDashAddConvertToC(u[27], 255, 90), self.testDashAddConvertToC(u[28], 255, 90), self.testDashAdd(u[29], 255, 90)],
                            'moisture': [self.testDash(u[36], 255), self.testDash(u[37], 255), self.testDash(u[38], 255), self.testDash(u[39], 255)]
                        },
                        'extra': {
                            'temp': [self.testDashAddConvertToC(u[33], 32767, 90), self.testDashAddConvertToC(u[34], 32767, 90), self.testDashAddConvertToC(u[35], 32767, 90)],
                            'humidity': [self.testDash(u[31], 255), self.testDash(u[32], 255)]
                        }
                    }
                })
                bin = file.read(52)

        return data
