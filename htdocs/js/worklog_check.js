
function createXMLHttpRequest()
{
	   XMLHttpReq=null;
	   if(window.ActiveXObject)
        { 
            XMLHttpReq=new ActiveXObject("Microsoft.XMLHTTP"); 
        }
        else if(window.XMLHttpRequest)
        { 
            XMLHttpReq=new XMLHttpRequest(); 
        } 
} 

function sum(obj,TaskID,User_SN,Project_Name,Submitter)
{
    var id = obj.name;
    var total=0;
    var space=0;
    var node_list = document.getElementsByTagName('input'); 
    for (var i = 0; i < node_list.length; i++) 
    { 
        var node = node_list[i]; 
        if (node.getAttribute('type') == 'text')
        { 
            if(node.id==id)
            {
                var current  = node.value;
                if (current.replace(/^\s+|\s+|-|\d+$/g,'')!='')
                {
                    obj.value = '';
                    alert('请正确填写内容!');
                    return false;
                }
                if (current.replace(/^\s+|\s+$/g,'')=='')
                {
                    space = 1;
                }
                else
                {
                    total = total + parseInt(node.value); 
                }
            }
        } 
    }  
    if(space==0)
    {
        if(total!=100)
        {
            var myvalue = 100 - total + parseInt(obj.value);
            alert('总和不为100!,建议为  ' + myvalue.toString() + ' ');
            obj.value = '';
            return false;
        }
    }
    else
    {
        if(total>100)
        {
            alert('总和已超过100!');
            obj.value = '';
            return false;
        }
    }

    createXMLHttpRequest(); 
    XMLHttpReq.onreadystatechange=function()
    {
        if (XMLHttpReq.readyState==4 && XMLHttpReq.status==200)
        {
            document.getElementById("total_" + id).innerText=total.toString();
            if (total==100)
            {
                document.getElementById("total_" + id).bgColor='ffffff';
            }
            else
            {
                document.getElementById("total_" + id).bgColor='ff0000';    
            }
        }
    }

    var tmp = "?action=ajax&taskid=" + TaskID;    
    tmp = tmp + "&User_SN=" + encodeURI(User_SN);
    tmp = tmp + "&Project_Name=" + encodeURI(Project_Name);
    tmp = tmp + "&Percent=" + encodeURI(obj.value);
    tmp = tmp + "&Submitter=" + encodeURI(Submitter);
    tmp = tmp + "&cache=" + Math.random();

	XMLHttpReq.open("GET","/idata/report/fill"+tmp,true);
	XMLHttpReq.send();

}
 
