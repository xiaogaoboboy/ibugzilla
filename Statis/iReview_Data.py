import time
import re
from datetime import datetime, timedelta
import MySQLdb



Start_Date = "2013-05-01"
End_Date   = "2013-06-30"

Days = ['2013-05-01','2013-06-10','2013-06-11','2013-06-12']
Work_Days=['2013-06-08','2013-06-09']

review_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='ireview',charset='utf8')
review_cursor = review_db.cursor()

user_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
user_cursor = user_db.cursor()

All_Day = []
All_Dep = {}
parten = re.compile(r'\.0$')

Date_tmp = datetime(int(Start_Date[0:4]), int(Start_Date[5:7]),int(Start_Date[8:10]),8,0,0)
Date_tmp_STR = datetime.strftime(Date_tmp,"%Y-%m-%d") 
while Date_tmp_STR <= End_Date:
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
print "iReview Statistics " +Start_Date + "---" + End_Date


DEP_NAME_LEN = 30
print ' '
print ' '
print ' '
print "Department_Name_Level_1" + " "*(DEP_NAME_LEN-len("Department_Name_Level_1")) + "\t\tAll_User\tReviews\t\tPreReviews\tUsage_Rate"
print '' 

DEP_1_Content = {}
DEP_2_Content = {}

# DEP1 
for a_dep in All_Dep.keys():

    All_Review_Task_ID = []
    All_PreReview_Comment_ID = []

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
            task_sql_1 =   "select ID  FROM iReviewTask_table  where SubmittedDate='" + a_day + "' and " 
            task_sql_1 =  task_sql_1 + " ( Author='" + USER_NAME + "'  or ReviewChairman='" + USER_NAME + "' or "
            task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',EssentialList,','))>0 or "
            task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',OtherList,','))>0  or  "
            task_sql_1 =  task_sql_1 + "Submitter='" + USER_NAME + "')" 

            task_sql_2 =   "select ID  FROM iPreReviewComment_table  where "
            task_sql_2 =  task_sql_2 + "Submitter='" + USER_NAME + "' and SubmittedDate='" + a_day + "'"
            
            records=0
            review_cursor.execute(task_sql_1)
            for ID in review_cursor:
                if ID[0] not in All_Review_Task_ID:
                    All_Review_Task_ID.append(ID[0])
                if records==0:
                    fill_count = fill_count + 1
                records += 1
                
            review_cursor.execute(task_sql_2)
            for ID  in review_cursor:
                if ID[0] not in All_PreReview_Comment_ID:
                    All_PreReview_Comment_ID.append(ID[0])
                if records==0:
                    fill_count = fill_count + 1
                records += 1
                
        if fill_count>0:
            all_fill = all_fill + 1.00
        #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
        all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
    DEP_1_Content.update({a_dep:len(All_Review_Task_ID)})
    print a_dep + " "*(DEP_NAME_LEN-len(a_dep)) + "\t\t" + str(all_user) + "\t\t" + str(len(All_Review_Task_ID)) + "\t\t" + str(len(All_PreReview_Comment_ID)) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100))

    
DEP_NAME_LEN = 35
print ' '
print ' '
print ' '
print "Department_Name_Level_2" + " "*(DEP_NAME_LEN-len("Department_Name_Level_2")) + "  \t\tAll_User\tReviews\t\tPreReviews\tUsage_Rate"
print ''
 
# DEP2 
for a_dep in All_Dep.keys():
    if DEP_1_Content[a_dep]==0:
        continue
    for a_dep2 in All_Dep[a_dep].keys():
        All_Review_Task_ID = []
        All_PreReview_Comment_ID = []
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
                task_sql_1 =   "select ID  FROM iReviewTask_table  where SubmittedDate='" + a_day + "' and " 
                task_sql_1 =  task_sql_1 + " ( Author='" + USER_NAME + "'  or ReviewChairman='" + USER_NAME + "' or "
                task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',EssentialList,','))>0 or "
                task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',OtherList,','))>0  or  "
                task_sql_1 =  task_sql_1 + "Submitter='" + USER_NAME + "')" 

                task_sql_2 =   "select ID  FROM iPreReviewComment_table  where "
                task_sql_2 =  task_sql_2 + "Submitter='" + USER_NAME + "' and SubmittedDate='" + a_day + "'"
                
                records=0
                review_cursor.execute(task_sql_1)
                for ID in review_cursor:
                    if ID[0] not in All_Review_Task_ID:
                        All_Review_Task_ID.append(ID[0])
                    if records==0:
                        fill_count = fill_count + 1
                    records += 1
                    
                review_cursor.execute(task_sql_2)
                for ID  in review_cursor:
                    if ID[0] not in All_PreReview_Comment_ID:
                        All_PreReview_Comment_ID.append(ID[0])
                    if records==0:
                        fill_count = fill_count + 1
                    records += 1
            if fill_count>0:
                all_fill = all_fill + 1.00
            #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
            all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
        tmp = a_dep + " | " + a_dep2 
        DEP_2_Content.update({tmp:len(All_Review_Task_ID)})
        print tmp + " "*(DEP_NAME_LEN-len(tmp)) + "\t\t" + str(all_user) + "\t\t" + str(len(All_Review_Task_ID)) + "\t\t" + str(len(All_PreReview_Comment_ID)) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100) )

DEP_NAME_LEN = 50
print ' '
print ' '
print ' '
print u"Department_Name_Level_3" + " "*(DEP_NAME_LEN-len("Department_Name_Level_3")) + "\t\tAll_User\tReviews\t\tPreReviews\tUsage_Rate"
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
            All_Review_Task_ID = []
            All_PreReview_Comment_ID = []
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
                    task_sql_1 =   "select ID  FROM iReviewTask_table  where SubmittedDate='" + a_day + "' and " 
                    task_sql_1 =  task_sql_1 + " ( Author='" + USER_NAME + "'  or ReviewChairman='" + USER_NAME + "' or "
                    task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',EssentialList,','))>0 or "
                    task_sql_1 =  task_sql_1 + " instr(CONCAT(',','" + USER_NAME + "',','),CONCAT(',',OtherList,','))>0  or  "
                    task_sql_1 =  task_sql_1 + "Submitter='" + USER_NAME + "')" 

                    task_sql_2 =   "select ID  FROM iPreReviewComment_table  where "
                    task_sql_2 =  task_sql_2 + "Submitter='" + USER_NAME + "' and SubmittedDate='" + a_day + "'"
                    
                    records=0
                    review_cursor.execute(task_sql_1)
                    for ID in review_cursor:
                        if ID[0] not in All_Review_Task_ID:
                            All_Review_Task_ID.append(ID[0])
                        if records==0:
                            fill_count = fill_count + 1
                        records += 1
                        
                    review_cursor.execute(task_sql_2)
                    for ID  in review_cursor:
                        if ID[0] not in All_PreReview_Comment_ID:
                            All_PreReview_Comment_ID.append(ID[0])
                        if records==0:
                            fill_count = fill_count + 1
                        records += 1
                if fill_count>0:
                    all_fill = all_fill + 1.00
                #print EName + '\t' +  str((fill_count+ 0.00)/len(All_Day))
                all_fill_per = all_fill_per + (fill_count+ 0.00)/len(All_Day)
            tmp = a_dep + " | " + a_dep2 + " | " +  a_dep3
            print tmp + " "*(DEP_NAME_LEN-len(tmp)) + "\t\t" + str(all_user) + "\t\t" + str(len(All_Review_Task_ID)) + "\t\t" + str(len(All_PreReview_Comment_ID)) + "\t\t" + parten.sub('',str(round(all_fill/all_user,4)*100)) 
 
 
 