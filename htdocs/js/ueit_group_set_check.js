function check(myform){
 var myvalue='';
 for (i=0; i<myform.field_ueit_Group_ID.length; i++)
 {
     if (myform.field_ueit_Group_ID[i].checked==true)
     {
        myvalue = myform.field_ueit_Group_ID[i].value;
     }
 }

 if(myvalue=='')
  {
   alert('Please select a group !');
   return false;
  }

  return true;
}