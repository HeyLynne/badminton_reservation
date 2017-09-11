# -*- coding: UTF-8 -*-

"""
    badminton.py : a small badminton reservation system
    Author : LynneZhou
    Email : lion19930924@163.com
    Date Created : 9/11/2017
    Python Version : 2.7
"""

import sys
import datetime

error_message = "> Error: the booking is invalid!";
accept_message = "> Success: the booking is accepted!";
confilict_message = "> Error: the booking conflicts with existing bookings!";
exist_message = "> Error: the booking being cancelled does not exist!";

cancel_mark = "C";

area_vec = ["A", "B", "C", "D"];

workday_cost = {"9~12":30, "12~18":50, "18~20":80, "20~22":60}

weekend_cost = {"9~12":40, "12~18":50, "18~22":60}

hour_low = 9
hour_high = 22

weekday_dedit = 0.5
weekend_dedit = 0.25

def IsDateValid(date_str):
    try:
        day = datetime.datetime.strptime(date_str, "%Y-%m-%d");
        return True;
    except:
        return False;

def SplitTimeRigion(time_rigion):
    times = time_rigion.split("~");
    hours = [];
    if len(times) != 2:
        return hours;
    for time in times:
        time_vec = time.split(":");
        if len(time_vec) != 2:
            return hours;
        if time_vec[1] != "00":
            return hours;
        try:
            hours.append(int(time_vec[0]));
        except:
            return hours;
    return hours;

def IsHourValid(hour_vec):
    if hour_vec[0] >= hour_vec[1]:
        return False;
    if hour_vec[0] < hour_low or hour_vec[1] > hour_high:
        return False
    return True;

def IsWorkDay(day):
    tmp = datetime.datetime.strptime(day, "%Y-%m-%d")
    d = tmp.weekday()
    if d == 5 or d == 6:
        return False
    return True

def IsTwoCoincide(vec1, vec2):
    if vec1[0] >= vec2[1] or vec1[1] <= vec2[0]:
        return False
    return True

def IsHourCoincide(hour_vec, area_account_time):
    for account_time in area_account_time:
        if IsTwoCoincide(hour_vec, account_time):
            return True
    return False

def CalCost(hour_vec, cost_vec):
    ori_start = hour_vec[0];
    ori_end = hour_vec[1];
    cost = 0;
    for cost_vec_key in cost_vec.keys():
        start_time = int(cost_vec_key.split("~")[0])
        end_time = int(cost_vec_key.split("~")[1])
        if ori_start >= end_time or ori_end <= start_time:
            continue;
        cost_start = max(ori_start, start_time);
        cost_end = min(ori_end, end_time);
        cost += (cost_end - cost_start) * cost_vec[cost_vec_key];
        ori_start = cost_start;
    return cost

def CalHourCost(hour_vec, is_work_day):
    cost = 0;
    if is_work_day:
        cost = CalCost(hour_vec, workday_cost);
    else:
        cost = CalCost(hour_vec, weekend_cost);
    return cost;

def Reserve(account, day, hour_vec, area):
    area_account = account[area];
    if day not in area_account.keys():
        area_account[day] = {};
        area_account[day]["time"] = [];
        # area_account[day]["income"] = 0;
        area_account[day]["breach"] = {};
    area_day_account = area_account[day];
    if IsHourCoincide(hour_vec, area_day_account["time"]):
        return False
    area_day_account["time"].append(hour_vec);
    return True;

def GenerateHourString(hour_vec):
    return "%s:00~%s:00" % (hour_vec[0], hour_vec[1]);

def Cancel(account, day, hour_vec, area):
    area_account = account[area];
    if day not in area_account.keys():
        return False;
    ori_start = hour_vec[0];
    ori_end = hour_vec[1];
    for time_rigion in area_account[day]["time"]:
        start_time = time_rigion[0];
        end_time = time_rigion[1];
        if ori_start == start_time and ori_end == end_time:
            is_work_day = IsWorkDay(day);
            cost = CalHourCost(hour_vec, is_work_day);
            hour_string = GenerateHourString(hour_vec);
            area_account[day]["breach"][hour_string] = 0;
            if is_work_day:
                area_account[day]["breach"][hour_string] = cost * weekday_dedit;
            else:
                area_account[day]["breach"][hour_string] = cost * weekend_dedit;
            area_account[day]["time"].remove(time_rigion);
            return True;
    return False

def CalDayAccount(day, account_time):
    print day
    is_work_day = IsWorkDay(day);
    total_cost = 0;
    for time_rigion in account_time:
        cost = 0;
        if is_work_day:
            cost = CalCost(time_rigion, workday_cost);
        else:
            cost = CalCost(time_rigion, weekend_cost);
        print u"> %s %d:00~%d:00 %d元" %(day, time_rigion[0], time_rigion[1], cost);
        total_cost += cost
    return total_cost;

def GetDayDedit(day, account_dedit):
    dedit = 0;
    for key in account_dedit.keys():
        dedit += account_dedit[key];
        print u"> %s %s 违约金 %d元" % (day, key, account_dedit[key]);
    return dedit;

def CalAccount(account):
    cost = 0
    dedit = 0
    for day in account.keys():
        account_time = account[day]["time"];
        day_cost = CalDayAccount(day, account_time);
        cost += day_cost;
        day_dedit = GetDayDedit(day, account[day]["breach"]);
        dedit += day_dedit
    return cost, dedit

def SettleAccount(account):
    print u"> 收入汇总\n> ---";
    total_account = 0
    for area in area_vec:
        print u"> 场地 %s" % (area);
        income, dedit = CalAccount(account[area]);
        print u"> 小计 %d元" % (income + dedit);
        print ">"
        total_account += income;
        total_account += dedit;
    print "> ---"
    print u"> 小计 %d元" %(total_account)

if __name__ == "__main__":
    account = {}
    account["A"] = {}
    account["B"] = {}
    account["C"] = {}
    account["D"] = {}
    while True:
        # if line is valid
        line = sys.stdin.readline();
        if line == "\n":
            break;
        lines = line.split();
        if len(lines) < 4 or len(lines) > 5:
            print error_message;
            continue;
        is_cancel = False;
        uid = lines[0];
        day = lines[1];
        time_rigion = lines[2];
        area = lines[3];
        if len(lines) == 5:
            if lines[4] == cancel_mark:
                is_cancel = True;
            else:
                print error_message;
                continue;
        if not IsDateValid(day):
            print error_message;
            continue;
        hour_rec = SplitTimeRigion(time_rigion);
        if len(hour_rec) == 0:
            print error_message;
            continue;
        if not IsHourValid(hour_rec):
            print error_message;
            continue;
        if area not in area_vec:
            print error_message;
            continue;
        # the booking is valid
        if not is_cancel:
            if Reserve(account, day, hour_rec, area):
                print accept_message
            else:
                print confilict_message
        else:
            if Cancel(account, day, hour_rec, area):
                print accept_message;
            else:
                print exist_message;
    SettleAccount(account);