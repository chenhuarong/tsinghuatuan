/**
 * Created with PyCharm.
 * User: LY
 * Date: 13-12-1
 * Time: 下午11:00
 * To change this template use File | Settings | File Templates.
 */

var book_status = 0;
var time_status = 0;
var place_status = 0;
var ticket_status = 0;
var details_status = 0;

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

document.getElementById('activitytime').onclick = function(){
    if(time_status){
        document.getElementById('timetrigger').className = "trigger";
        document.getElementById('timedetails').style.display = "none";
        time_status = 0;
    }
    else{
        document.getElementById('timetrigger').className = "trigger active";
        document.getElementById('timedetails').style.display = "block";
        time_status = 1;
    }
}

document.getElementById('place').onclick = function(){
    if(place_status){
        document.getElementById('placetrigger').className = "trigger";
        document.getElementById('placedetails').style.display = "none";
        place_status = 0;
    }
    else{
        document.getElementById('placetrigger').className = "trigger active";
        document.getElementById('placedetails').style.display = "block";
        place_status = 1;
    }
}

document.getElementById('ticket').onclick = function(){
    if(ticket_status){
        document.getElementById('tickettrigger').className = "trigger";
        document.getElementById('ticketdetails').style.display = "none";
        ticket_status = 0;
    }
    else{
        document.getElementById('tickettrigger').className = "trigger active";
        document.getElementById('ticketdetails').style.display = "block";
        ticket_status = 1;
    }
}

document.getElementById('content').onclick = function(){
    if(details_status){
        document.getElementById('contenttrigger').className = "trigger";
        document.getElementById('contentdetails').style.display = "none";
        details_status = 0;
    }
    else{
        document.getElementById('contenttrigger').className = "trigger active";
        document.getElementById('contentdetails').style.display = "block";
        details_status = 1;
    }
}