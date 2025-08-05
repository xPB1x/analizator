import re


def sum_time(times):
    total = [0, 0, 0]
    for time in times:
        time = [int(x) for x in time.split(':')]
        for i in range(3):
            if i == 0:
                total[0] += time[0]
            else:
                sm = total[i] + time[i]
                if sm < 60:
                    total[i] = sm
                else:
                    total[i] = sm - 60
                    total[i-1] += 1

    return ':'.join([str(x) for x in total])


def substraction_time(time1, time2):
    result = [0, 0, 0]
    time1 = [int(x) for x in time1.split(':')]
    time2 = [int(x) for x in time2.split(':')]

    for i in range(3):
        dif = time1[i] - time2[i]
        if dif < 0:
            result[i] = 60 + dif
            result[i-1] -= 1
        else:
            result[i] = dif

    return ':'.join([str(x) for x in result])


def find_first_control(sportsman_info: list[str]):
    for i in range(len(sportsman_info)):
        if re.search(r'\(\s*\d+\s*\)', sportsman_info[i]):
            return i

def find_first_control2(sportsman_info: list[str]):
    for i in range(len(sportsman_info)):
        if re.search(r'\[\s*\d+\s*', sportsman_info[i]):
            return i


if __name__ == '__main__':
    print(substraction_time('00:48:51', '00:48:36'))