     function SubmitValue()
     {
        var aryInput=document.body.getElementsByTagName("Input");
        var allGroupID='';
        var allGroupName='';
        for(var i=0;i<aryInput.length;i++)
        {
            if(aryInput[i].type=="checkbox")
            {
                if(aryInput[i].checked)
                {
                    allGroupID = allGroupID + '  ' + aryInput[i].id;
                    if(allGroupName=='')
                    {
                        allGroupName = aryInput[i].value;
                    }
                    else
                    {
                        allGroupName = allGroupName + ' ; ' + aryInput[i].value;
                    }
                }
            }
        }
        window.opener.SetGroupIDValue(allGroupID);
        window.opener.SetGroupNameValue(allGroupName);
        window.close();
     }
