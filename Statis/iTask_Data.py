import time
import re
from datetime import datetime, timedelta
import MySQLdb



Start_Date = "2013-05-01"
End_Date   = "2013-06-30"

Days = ['2013-05-01','2013-06-10','2013-06-11','2013-06-12']
Work_Days=['2013-06-08','2013-06-09']

task_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='itask',charset='utf8')
task_cursor = task_db.cursor()

user_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
user_cursor = user_db.cursor()

All_Day = []
All_Dep = {}

parten = re.compile(r'\.0$')

Date_tmp = datetime(int(Start_Date[0:4]), int(Start_Date[5:7]),int(Start_Date[8:10]),8,0,0)
Date_tmp_STR = datetime.strftime(Date_tmp,"%Y-%m-%d") 
while Date_tmp_STR <= End_Date:
    myWeek= int(datetime.strftime(Date_tmp,"%w"))
    if myWeek==0:
        myWeek=7
    if myWeek in [6,7] and Date_tmp_STR in Work_Days:
        All_Day.append(Date_tmp_STR)
    if myWeek in [1,2,3,4,5] and Date_tmp_STR not in Days:
        All_Day.append(Date_tmp_STR)
    Date_tmp = Date_tmp + timedelta(days =1)
    Date_tmp_STR = datetime.strftime(Date_tmp,"%Y-%m-%d") 


dep_sql = "select distinct DepID1,DepID2,DepID3 from User_List where Status='" + u"在职" + "'"
user_cursor.execute(dep_sql)
for  DepID1,DepID2,DepID3  in user_cursor:
    if DepID1 not in All_Dep.keys():
        All_Dep.update({DepID1:{DepID2:[DepID3]}})
    else:
        tmp_1 = All_Dep[DepID1]
        if DepID2 not in tmp_1.keys():
            tmp_1.update({DepID2:[DepID3]})
            All_Dep.update({DepID1:tmp_1})
        else:
            tmp_2 = tmp_1[DepID2]
            tmp_2.append(DepID3)
            tmp_1.update({DepID2:tmp_2})
            All_Dep.update({DepID1:tmp_1})


print ''
print ''            
print "iTask/iWorklog Statistics " +Start_Date + "---" + End_Date


DEP_NAME_LEN = 30
DEP_1_Content = {}
DEP_2_Content = {}

print ' '
print "Department_Name_Level_1" + " "*(DEP_NAME_LEN-len("Department_Name_Level_1")) + "\tAll_User\tUsage_Rate\tSubmit_Rate"
print '' 

# DEP1 
for a_dep in All_Dep.keys():
    user_sql = "select EName,DepID1,DepID2 from User_List where DepID1='" + a_dep + "' and  Status='" + u"在职" + "'"
    all_user = 0
    all_fill_per = 0.00
    all_fill=0.00
    user_cursor.execute(user_sql)
    for  EName,DepID1,DepID2  in user_cursor:
        fill_count = 0
        all_user = all_user + 1
        for a_day in All_Day:
            USER_NAME = EName.replace(' ','.').lower()
            task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + a_day + " 00:00:00' and t2.SubmittedDate<='" + a_day + " 23:59:59' "
            task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + a_day + " 00:00:00' and t3.SubmittedDate<='" + a_day + " 23:59:59'"
            task_cursor.execute(task_sql_1)
            if task_cursor.fetchone()[0]>0:
                fill_count = fill_count + 1
            else:
                task_cursor.execute(task_sql_2)
                if task_cursor.fetchone()[0]>0:
                    fill_count = fill_count + 1
        if fill_count>0:
            all_fill = all_fill + 1.00
        #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
        all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
    DEP_1_Content.update({a_dep:all_fill})
    print a_dep + " "*(DEP_NAME_LEN-len(a_dep)) + "\t" + str(all_user) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100)) + "\t\t" + parten.sub('',str(round(all_fill_per/all_user,4)*100))



DEP_NAME_LEN = 50
print ' '
print u"Department_Name_Level_2" + " "*(DEP_NAME_LEN-len("Department_Name_Level_2")) + "\tAll_User\tUsage_Rate\tSubmit_Rate"
print ''

# DEP2 
for a_dep in All_Dep.keys():
    if DEP_1_Content[a_dep]==0:
        continue
    for a_dep2 in All_Dep[a_dep].keys():
        user_sql = "select EName,DepID1,DepID2 from User_List where DepID1='" + a_dep + "' and  DepID2='" + a_dep2  + "' and  Status='" + u"在职" + "'"
        all_user = 0
        all_fill_per = 0.00
        all_fill=0.00
        user_cursor.execute(user_sql)
        for  EName,DepID1,DepID2  in user_cursor:
            fill_count = 0
            all_user = all_user + 1
            for a_day in All_Day:
                USER_NAME = EName.replace(' ','.').lower()
                task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + a_day + " 00:00:00' and t2.SubmittedDate<='" + a_day + " 23:59:59' "
                task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + a_day + " 00:00:00' and t3.SubmittedDate<='" + a_day + " 23:59:59'"
                if a_dep=='Product' and a_dep2=='PM':
                    a_day = datetime(int(a_day[0:4]), int(a_day[5:7]),int(a_day[8:10]),8,0,0)
                    myWeek= int(datetime.strftime(a_day,"%w"))
                    if myWeek==0:
                        myWeek=7
                    Week_Start_DB = datetime.strftime(a_day - timedelta(days =(myWeek-1)),"%Y-%m-%d")  + ' 00:00:00'
                    Week_END_DB = datetime.strftime(a_day + timedelta(days =(7-myWeek)),"%Y-%m-%d")   + ' 23:59:59'
                    task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + Week_Start_DB + "' and t2.SubmittedDate<='" + Week_END_DB + "' "
                    task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + Week_Start_DB + "' and t3.SubmittedDate<='" + Week_END_DB + "' "
                task_cursor.execute(task_sql_1)
                if task_cursor.fetchone()[0]>0:
                    fill_count = fill_count + 1
                else:
                    task_cursor.execute(task_sql_2)
                    if task_cursor.fetchone()[0]>0:
                        fill_count = fill_count + 1
            if fill_count>0:
                all_fill = all_fill + 1.00
            #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
            all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
        tmp = a_dep + " | " + a_dep2 
        DEP_2_Content.update({tmp:all_fill})
        print tmp + " "*(DEP_NAME_LEN-len(tmp)) + "\t" + str(all_user) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100)) + "\t\t" + parten.sub('',str(round(all_fill_per/all_user,4)*100))


DEP_NAME_LEN = 50 
print ' '
print u"Department_Name_Level_3" + " "*(DEP_NAME_LEN-len("Department_Name_Level_3")) + "\tAll_User\tUsage_Rate\tSubmit_Rate"
print ''

# DEP3 
for a_dep in All_Dep.keys():
    if DEP_1_Content[a_dep]==0:
        continue
    for a_dep2 in All_Dep[a_dep].keys():
        tmp = a_dep + " | " + a_dep2 
        if DEP_2_Content[tmp]==0:
            continue
        for a_dep3 in All_Dep[a_dep][a_dep2]:
            user_sql = "select EName,DepID1,DepID2 from User_List where DepID1='" + a_dep + "' and  DepID2='" + a_dep2  + "' and  DepID3='" + a_dep3  + "' and  Status='" + u"在职" + "'"
            all_user = 0
            all_fill_per = 0.00
            all_fill=0.00
            user_cursor.execute(user_sql)
            for  EName,DepID1,DepID2  in user_cursor:
                fill_count = 0
                all_user = all_user + 1
                for a_day in All_Day:
                    USER_NAME = EName.replace(' ','.').lower()
                    task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + a_day + " 00:00:00' and t2.SubmittedDate<='" + a_day + " 23:59:59' "
                    task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + a_day + " 00:00:00' and t3.SubmittedDate<='" + a_day + " 23:59:59'"
                    if a_dep=='Product' and a_dep2=='PM':
                        a_day = datetime(int(a_day[0:4]), int(a_day[5:7]),int(a_day[8:10]),8,0,0)
                        myWeek= int(datetime.strftime(a_day,"%w"))
                        if myWeek==0:
                            myWeek=7
                        Week_Start_DB = datetime.strftime(a_day - timedelta(days =(myWeek-1)),"%Y-%m-%d")  + ' 00:00:00'
                        Week_END_DB = datetime.strftime(a_day + timedelta(days =(7-myWeek)),"%Y-%m-%d")   + ' 23:59:59'
                        task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + Week_Start_DB + "' and t2.SubmittedDate<='" + Week_END_DB + "' "
                        task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + Week_Start_DB + "' and t3.SubmittedDate<='" + Week_END_DB + "' "
                    task_cursor.execute(task_sql_1)
                    if task_cursor.fetchone()[0]>0:
                        fill_count = fill_count + 1
                    else:
                        task_cursor.execute(task_sql_2)
                        if task_cursor.fetchone()[0]>0:
                            fill_count = fill_count + 1
                if fill_count>0:
                    all_fill = all_fill + 1.00
                #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
                all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
            tmp = a_dep + " | " + a_dep2 + " | " +  a_dep3
            print tmp + " "*(DEP_NAME_LEN-len(tmp)) + "\t" + str(all_user) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100)) + "\t\t" + parten.sub('',str(round(all_fill_per/all_user,4)*100))
 
 
 