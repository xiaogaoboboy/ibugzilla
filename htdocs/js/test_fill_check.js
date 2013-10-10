function check(myform){
 var myvalue='';
 for (i=0; i<myform.field_test_fill_Test_Result.length; i++)
 {
     if (myform.field_test_fill_Test_Result[i].checked==true)
     {
        myvalue = myform.field_test_fill_Test_Result[i].value;
     }
 }

 if(myvalue=='')
  {
   alert('Please select a test result!');
   return false;
  }


 if((myvalue=='NE' || myvalue=='Postpone') && myform.field_test_fill_Notes.value.replace(/^\s+|\s+$/g,'').length==0)
  {
   alert('请填写测试说明!');
   return false;
  }

 if(myvalue=='fail' && myform.field_test_fill_CRID.value.replace(/^\s+|\s+$/g,'')==''  && myform.field_test_fill_Notes.value.replace(/^\s+|\s+$/g,'').length==0)
  {
   alert('请填写测试说明!');
   return false;
  }

 if(myform.field_test_fill_Notes.value.length>400)
  {
   alert('测试说明要少于 400 字!');
   return false;
  }
  
  return true;
}