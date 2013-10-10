
function AddList(type){
 for (i=1;i<=30;i++){
  if (document.all[type +"_LL"+i]){
        
  	if (document.all[type +"_LL"+i].style.display=="none"){
  	   document.all[type +"_LL"+i].style.display="";
  	break;
	}
   }
  }
}

function DelList(type,ItemNum){
 for (i=ItemNum;i<=30;i++){
  if (document.all[type +"_LL"+(i+1)]){
  	if (document.all[type +"_LL"+(i+1)].style.display!="none"){
		document.all["field_test_request_" + type + "_PRJ_ID_"+i].value=document.all["field_test_request_" + type + "_PRJ_ID_"+(i+1)].value
		document.all["field_test_request_" + type + "_PRJ_Name_"+i].value=document.all["field_test_request_" + type + "_PRJ_Name_"+(i+1)].value
		document.all["field_test_request_" + type + "_PRJ_Description_"+i].value=document.all["field_test_request_" + type + "_PRJ_Description_"+(i+1)].value
  	}
        else{
                "field_test_request_" + type + "_PRJ_ID_"+i
		document.all[type +"_LL"+i].style.display="none"
		document.all["field_test_request_" + type + "_PRJ_ID_"+i].value=''
		document.all["field_test_request_" + type + "_PRJ_Name_"+i].value=''
		document.all["field_test_request_" + type + "_PRJ_Description_"+i].value=''
		break;
	}
   }
   else{
	document.all[type +"_LL"+i].style.display="none"
	document.all["field_test_request_" + type + "_PRJ_ID_"+i].value=''
	document.all["field_test_request_" + type + "_PRJ_Name_"+i].value=''
	document.all["field_test_request_" + type + "_PRJ_Description_"+i].value=''
    }   
  }
}
