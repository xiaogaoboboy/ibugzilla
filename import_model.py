
import re
import MySQLdb
import os
import pickle
from datetime import datetime, timedelta

class Import_Data(object):
    
    @classmethod
    def GetAllfile(File_List, mypath):
        if mypath:
            a=os.listdir(mypath)
            mydir=[x for x in a if os.path.isdir(mypath+'/'+x)]
            myfile=[x for x in a if os.path.isfile(mypath+'/'+x)]
            for  tmp in myfile:
                x, y = os.path.splitext(mypath + '\\' + tmp)
                if y=='.xls' or y=='.xlsx':
                    File_List.append(mypath + '\\' + tmp)
            for  tmp in mydir:
                self.GetAllfile(File_List, mypath+'\\'+tmp)
    @classmethod
    def go(self,): 
        import python_excel
        File_List = []
        current_pach= os.getcwd()
        self.GetAllfile(File_List, current_pach)
        for a_file in File_List:
            if os.path.exists(a_file):
                aExcel_Mod = python_excel.excel_mod(a_file)
                for aSheet_Index in range(0, aExcel_Mod.getsheetcount()): 
                    aSheet  = aExcel_Mod.workbook.Sheets[aSheet_Index]
                    row_length = aSheet.UsedRange.Rows.Count
                    row_col =  aSheet.UsedRange.Columns.Count
                    aTable = aExcel_Mod.gettable(aSheet_Index,1,1,row_length,row_col)
                    for mycol in range(6,row_col):
                        if aSheet.Cells(0,mycol).value:
                            print aSheet.Cells(0,mycol).value
                aExcel_Mod.close()


