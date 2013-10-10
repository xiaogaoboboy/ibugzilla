#*_* encoding:utf-8 *_*
'''*************************************
excel与python数据间的通用接口
*****************************************'''
from win32com.client import Dispatch

class excel_mod:
    def __init__(self,filename=None):
        self.xlApp = Dispatch('Excel.Application')
        if filename :
            self.filename=filename
            self.workbook=self.xlApp.Workbooks.Open(filename)
        else:
            self.filename="new_excle.xls"
            self.workbook=self.xlApp.Workbooks.Add()

    def show (self):
        self.xlApp.Visible=1

    def hide (self):
        self.xlApp.Visible=0
  
    def save(self,newfilename=None):
        if newfilename:
            self.filename = newfilename
            self.workbook.SaveAs(newfilename)
        else:
            self.workbook.Save()

    def close(self):
        self.workbook.Close(SaveChanges=0)
        del self.xlApp
     
    def addsheet(self,sheetname=None):
        sht=self.workbook.Sheets.Add()
        if sheetname:
            try :
                sht.Name=sheetname
            except :
                print 'the add sheet is already exist '
                
        else:
            pass
        return sht
        
    def getsheetcount(self):
        return self.workbook.Sheets.Count
        
    def setsheetname(self,sheet,newname):
        sht=self.seletsheet(sheet)
        if sht :
            sht.Name=newname
            return True
        else:
            return False
    def delsheet(self,sheet):
        sht=self.seletsheet(sheet)
        try:
            sht.Delete()
            return True
        except:
            return False
    def seletsheet(self,sheet):
        if type(sheet).__name__ == 'str':
            try :
                sht=self.workbook.Worksheets(sheet)
                return sht
            except:
                print 'no sheet name is %s'%sheet
                return None
        elif type(sheet).__name__ == 'int':
            try:
                sht=self.workbook.Sheets[sheet]
                return sht
            except IndexError :
                print 'the sheet num is out of range'
                return None
        else :
            print 'sheet mast is str or int'
            return None
    def mergecells (self,sheet,row1,col1,row2,col2):
        sht=self.seletsheet(sheet)
        if sht:
            pass
        else:
            return None
        
        sht.Range(sht.Cells(row1,col1),sht.Cells(row2,col2)).Merge()
        
    def getcell(self,sheet,row,col):
        sht=self.seletsheet(sheet)
        #print sht
        if sht:
            pass
        else:
            print 'no sheet'
            return None
        try :
            return sht.Cells(row,col).Value
        except:
            print 'the cell is not in sheet'
            return None
    def setcell(self,sheet,row,col,value):
        sht=self.seletsheet(sheet)
        if sht:
            pass
        else:
            return False
            
        try :
            sht.Cells(row,col).Value=value
            return True
        except:
            print 'the cell is not in sheet'
            return False
    def gettable(self,sheet,row1,col1,row2,col2):
        sht=self.seletsheet(sheet)
        if sht:
            pass
        else:
            return None
            
        try :
            return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value
        except :
            print 'input row1 col1 row2 col2 is error'
            return None
    def settable(self,sheet,row1,col1,row2,col2,tump):
        ''' the tump size and tavle size is mast same'''
        sht=self.seletsheet(sheet)
        if sht :
            pass
        else:
            return False
        try :
            sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value=tump
            return True
        except:
            return False
    def getusedRange(self,sheet):
        sht=self.seletsheet(sheet)
        if sht:
            pass
        else:
            return None
        return sht.UsedRange.Rows

    def setfontcolor(self,sheet,row,col,color):
        sht=self.seletsheet(sheet)
        if sht:
            pass
        else:
            return False
        try :
            sht.Cells(row,col).Font.Color=color
            return True
        except:
            return False
if __name__=='__main__':
    p=excel_mod(r'D:\test.xls')
    p.show()
    a=p.getusedRange("abc")
    print a
    bb=raw_input(">ss")
    a=p.getusedRange(bb)
    print a
    raw_input(">ss")
    p.save()
    p.close()
