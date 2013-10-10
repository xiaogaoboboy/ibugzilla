function tips_pop(){
  var MsgPop=document.getElementById("winpop");
  var popH=parseInt(MsgPop.style.height);//将对象的高度转化为数字
   if (popH==0){
   MsgPop.style.display="block";//显示隐藏的窗口
  show=setInterval("changeH('up')",2);
   }
  else { 
   hide=setInterval("changeH('down')",2);
  }
}
function changeH(str) {
 var MsgPop=document.getElementById("winpop");
 var popH=parseInt(MsgPop.style.height);
 if(str=="up"){
  if (popH<=150){
  MsgPop.style.height=(popH+4).toString()+"px";
  }
  else{  
  clearInterval(show);
  }
 }
 if(str=="down"){ 
  if (popH>=4){  
  MsgPop.style.height=(popH-4).toString()+"px";
  }
  else{ 
  clearInterval(hide);   
  MsgPop.style.display="none";  //隐藏DIV
  }
 }
}
