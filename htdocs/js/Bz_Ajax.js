
function createXMLHttpRequest()
{
      //alert("createXMLHttpRequest");	
	XMLHttpReq=null;
	if(window.ActiveXObject)
        { 
            XMLHttpReq=new ActiveXObject("Microsoft.XMLHTTP"); 
			//alert("IE");	
        }
	else if(window.XMLHttpRequest)
        { 
            XMLHttpReq=new XMLHttpRequest(); 
		//alert("Common Explorer");	
        } 	 
	else
		{
		alert("not support XMLHttpRequest");
		}
	

} 



function test()
{
    alert("test");
}

function Bz_QueryTree(ID, name)
{
    //document.all["mainframe" ].innerHTML="";	
	var x=document.getElementById("mainframe").innerHTML="";	

	//alert("createXMLHttpRequest");
    createXMLHttpRequest();      		
	
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             //document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
			 document.getElementById("mainframe").innerHTML=XMLHttpReq.responseText;
        }
    }
    //var tmp = "?bugz_query="+name;
    var tmp = "?bz_ajax=bz_ajax_tree";
	tmp = tmp + "&ID=" + ID;
	tmp = tmp + "&name=" + name;

	//alert(tmp);
    //XMLHttpReq.open("GET","http://itest-center/iTest/sql/Bz_Ajax_QueryTree"+tmp,true);	

    //XMLHttpReq.open("GET","http://imanage.sprd.com/idata/Bugzilla/query/Bz_Ajax_QueryTree"+tmp,true);
    
    url = "http://tracsrv/idata/Bugzilla/query/Bz_Ajax_QueryTree"+tmp
    XMLHttpReq.open("GET",url,true);	
    
  // alert(url);
	//alert(XMLHttpReq.responseText);
    XMLHttpReq.send();
	//alert("ok");
	
}


function Bz_DelOneQueryItem(ID)
{   
    alert(ID);
    //document.all["mainframe" ].innerHTML="";
    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             //document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
             //alert("echo");
        }else{
             //alert(XMLHttpReq.readyState);
			 //alert(XMLHttpReq.status);
   		}
		
    }
    var tmp = "?bz_ajax=bz_ajax_del";
	tmp = tmp + "&ID=" + ID;
	//alert(tmp);
    //'http://itest-center/iTest/sql/bugzilla_test?bugz_query=bugz_Del&name='+name
    
    //url = "http://itest-center/iTest/sql/QueryManager"+tmp  
    //url = "http://imanage.sprd.com/idata/Bugzilla/query/QueryManager"+tmp  
    url = "http://tracsrv/idata/Bugzilla/query/QueryManager"+tmp  
    //alert(url);
	
    XMLHttpReq.open("GET",url,true);	

    XMLHttpReq.send();
	
}


function Bz_DelQueryList(ID) {
   var msg = "Del ID=" + ID +"? Plz Confirm!";
    if (confirm(msg)==true){

	    Bz_DelOneQueryItem(ID);
       return true;
   }else{
       return false;
   }
}

function Bz_QueryActionItem(ID, action)
{   
	createXMLHttpRequest(); 
	XMLHttpReq.onreadystatechange=function()
	{
	    if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
	    {
	    }else{
	    }		
	}

	var tmp = "?action=" + action;
	tmp = tmp + "&ID=" + ID;
	url = "http://tracsrv/idata/Bugzilla/query/QueryManager"+tmp  
	XMLHttpReq.open("GET",url,true);	
	XMLHttpReq.send();
	alert(action+ " ID=" + ID +" successfully!");
}

function Bz_QueryAction(ID, action) {
   var msg = action+ " ID=" + ID +"? Plz Confirm!";
    if (confirm(msg)==true){
	    Bz_QueryActionItem(ID, action);
       return true;
   }else{
       return false;
   }
}



function Bz_ActionItem(ID, action, path_info)
{   
	createXMLHttpRequest(); 
	XMLHttpReq.onreadystatechange=function()
	{
		if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
		{
		}
		else
		{
		}
		
	}
	var tmp = "?action=" + action;;
	tmp = tmp + "&ID=" + ID;	
       url = "http://tracsrv/idata/Bugzilla/query/"+path_info+tmp
	//alert(url);
	XMLHttpReq.open("GET",url,true);	
	XMLHttpReq.send();	
	alert(action+ " ID=" + ID +" successfully!");
}


function Bz_Action(ID, action, path_info) {
   var msg = action+ " ID=" + ID +"? Plz Confirm!";
    if (confirm(msg)==true){
	    Bz_ActionItem(ID, action, path_info);
       return true;
   }else{
       return false;
   }
}


function Bz_Add_aFiled(ID)
{   
	createXMLHttpRequest(); 
	XMLHttpReq.onreadystatechange=function()
	{
		if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
		{
		}
		else
		{
		}
		
	}
	var tmp = "?LastFeildID=" + ID;
	//tmp = tmp + "&LastFeildID=" + ID;	
    url = "http://tracsrv/idata/Bugzilla/query/"+"Bz_QueryManage"+tmp
	//alert(url);
	XMLHttpReq.open("GET",url,true);	
	XMLHttpReq.send();	
	alert(send+ " url=" + url +" successfully!");
}

function Bz_add_a_fieldgroup(id) { 
        //$("#Group1").show();	
        alert('Bz_add_a_fieldgroup: '+id);
		Bz_Add_aFiled(id);
        if (id=='1')
        { 
           //$("#Group1").show();
        }	
    		
}

function Bz_add_field() { 
	alert('Bz_add_field: ');
    var row = document.getElementById('custom_search_last_row');
	alert('row: '+row);
    var clone = row.cloneNode(true);
    alert('clone: '+clone);
	
    //_cs_fix_ids(clone);
   
    // We only want one copy of the buttons, in the new row. So the old
    // ones get deleted.
    var op_button = document.getElementById('op_button');
    row.removeChild(op_button);
    //var cp_button = document.getElementById('cp_container');
    row.removeChild(cp_button);
    var add_button = document.getElementById('add_button');
    row.removeChild(add_button);
    //_remove_any_all(clone);

    // Always make sure there's only one row with this id.
    row.id = null;
    row.parentNode.appendChild(clone);
    //fix_query_string(row);
    return clone;
	
}	
function Bz_add_field2() { 
	alert('Bz_add_field: ');
	var LastFeildID = document.getElementById("LastFeildID").value;

	alert('LastFeildID: '+LastFeildID);	

	//var FreeFieldId = document.getElementById("FreeFieldId").value;

	//alert('FreeFieldId: '+FreeFieldId);	
		
		
    //document.all["mainframe" ].innerHTML="";	
	var x=document.getElementById("mainframe").innerHTML="";	

	//alert("createXMLHttpRequest");
    createXMLHttpRequest();      		
	
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
             //document.all["mainframe" ].innerHTML=XMLHttpReq.responseText;
			 document.getElementById("mainframe").innerHTML=XMLHttpReq.responseText;
        }
    }
	var tmp = "?LastFeildID=" + LastFeildID;
    url = "http://tracsrv/idata/Bugzilla/query/"+"Bz_Field"+tmp

    XMLHttpReq.open("GET",url,true);	
    
    XMLHttpReq.send();
	alert("url"+url);
    		
}


function Bz_add_group() { 
	alert("Bz_add_group");
	$("#GroupRule5").show();
	$("#GroupRule15").show();	
}

function Bz_ChooseGroup() { 
	//alert('Bz_ChooseGroup');

        if ($("#GroupNum").val()=='0')
        { 
           $("#GroupRule5").hide();
           $("#GroupRule15").hide();
        }	
        if ($("#GroupNum").val()=='1')
        { 
           $("#GroupRule5").show();
           $("#GroupRule15").hide();
        }
        if ($("#GroupNum").val()=='2')
        { 
           $("#GroupRule5").show();
           $("#GroupRule15").show();
        } 
} 

function Bz_RemindTypeChange() { 
	//alert('Bz_RemindTypeChange');
	
        if ($("#RemindType").val()=='M')
        { 
           $("#week_div").hide();
           $("#month_div").show();
           $("#RemindInterval").show();
           $("#RemindStartDate").show();
           $("#RemindEndDate").show();
           $("#RemindCounter").show();
        }
        if ($("#RemindType").val()=='W')
        { 
           $("#week_div").show();
           $("#month_div").hide();
           $("#RemindInterval").show();
           $("#RemindStartDate").show();
           $("#RemindEndDate").show();
           $("#RemindCounter").show();
        } 
        if ($("#RemindType").val()=='D')
        { 
           $("#week_div").show();
           $("#month_div").hide();
           $("#RemindInterval").show();
           $("#RemindStartDate").show();
           $("#RemindEndDate").show();
           $("#RemindCounter").show();
        } 
        if ($("#RemindType").val()=='F')
        { 
           $("#RemindStartDate").show();
           $("#RemindInterval").hide();
           $("#RemindEndDate").hide();
           $("#RemindCounter").hide();
           $("#month_div").hide();
           $("#week_div").hide();
        } 
        if ($("#RemindType").val()=='')
        { 
           $("#week_div").hide();
           $("#month_div").hide();
           $("#RemindInterval").hide();           
           $("#RemindStartDate").hide();
           $("#RemindEndDate").hide();
           $("#RemindCounter").hide();
        } 
} 




