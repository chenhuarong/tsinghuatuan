/**
 * Created with PyCharm.
 * User: LY
 * Date: 13-12-1
 * Time: 下午11:00
 * To change this template use File | Settings | File Templates.
 */
var maxtime = 60*60;
var book_status = 0;

function CountDown()
{
    if(maxtime>=0){
        hours = Math.floor(maxtime/3600);
        minutes = Math.floor(maxtime/60);
        seconds = Math.floor(maxtime%60);
        msg = "距离结束还有 "+minutes+" 分 "+seconds+" 秒";
        document.all["timer"].innerHTML=msg;
        --maxtime;
    }
    else{
        clearInterval(timer);
        //
    }
}

timer = setInterval("CountDown()",1000);

document.getElementById('booktime').onclick = function(){
    if(book_status){
        document.getElementById('booktrigger').className = "trigger";
        document.getElementById('bookdetails').style.display = "none";
        book_status = 0;
    }
    else{
        document.getElementById('booktrigger').className = "trigger active";
        document.getElementById('bookdetails').style.display = "block";
        book_status = 1;
    }
}