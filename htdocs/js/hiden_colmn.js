function fnShowHide( bVis)
{   var oTable = $('#myitemTable').dataTable(); 
     for (i=1; i<=12; i++)
    {
        oTable.fnSetColumnVis( i, bVis ? false : true ); 
    }
} 
