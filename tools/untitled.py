import re
import time 


def convert_gmt_to_13stamp(t):

    # confirm this param
    if not isinstance(t,str):
        t = str(t)

    # get num behind dot 
    try:
        num_behind_point = re.findall(r'\.(\d+)',t)[0]
        if len(num_behind_point) ==1:
            num_behind_point = num_behind_point + '00'
        elif len(num_behind_point) ==2:
            num_behind_point = num_behind_point + '0'
        elif len(num_behind_point)>2:
            num_behind_point = num_behind_point[:3]
    except:
        num_behind_point = '000'

    # convert time tuple to stamp
    num_list = list(map(lambda x:int(float(x)),re.findall(r'([\d\.]+)',t)))
    time_tuple = tuple(num_list[:6]+[0,0,0])
    timestamp = int(str(int(time.mktime(time_tuple)))[:10] + num_behind_point)

    # take out timezone in timestamp
    time_zone_h = time.strftime('%z', time.localtime())[:3]
    h = int(re.findall(r'(\d+)',time_zone_h)[0])
    ss = h * 3600 * 1000
    if '+' in time_zone_h:
        timestamp = timestamp + ss
    elif '-' in time_zone_h:
        timestamp = timestamp - ss

    return str(timestamp)

if __name__ == '__main__':
    t = "2018-10-17T18:43:03.213"

    print(convert_gmt_to_13stamp(t))

