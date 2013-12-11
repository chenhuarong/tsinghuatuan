/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-12-3
 * Time: 下午11:12
 */

function clearActs() {
    $('#tbody-activities').html('');
}

function getSmartStatus(act) {
    if (act.status == 0) {
        return '未发布';
    } else if (act.status == 1) {
        var now = new Date();
        if (now < act.book_start) {
            return '等待订票';
        } else if (now < act.book_end) {
            return '正在订票';
        } else if (now < act.start_time) {
            return '正在出票';
        } else if (now < act.end_time) {
            return '活动进行中';
        } else {
            return '已结束';
        }
    } else {
        return '未知';
    }
}

function wrapTwoDigit(num) {
    if (num < 10) {
        return '0' + num;
    } else {
        return num;
    }
}

function getChsDate(dt) {
    return wrapTwoDigit(dt.getDate()) + '日';
}

function getChsMonthDay(dt) {
    return (dt.getMonth() + 1) + '月' + getChsDate(dt);
}

function getChsFullDate(dt) {
    return dt.getFullYear() + '年' + getChsMonthDay(dt);
}

function getChsDay(dt) {
    var dayMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return dayMap[dt.getDay()];
}

function getTimeStr(dt) {
    return wrapTwoDigit(dt.getHours()) + ':' + wrapTwoDigit(dt.getMinutes());
}

function isSameYear(d1, d2) {
    return d1.getFullYear() == d2.getFullYear();
}

function isSameMonth(d1, d2) {
    return isSameYear(d1, d2) && (d1.getMonth() == d2.getMonth());
}

function isSameDay(d1, d2) {
    return isSameYear(d1, d2) && isSameMonth(d1, d2) && (d1.getDate() == d2.getDate());
}

function getSmartTimeRange(start_time, end_time) {
    var result = getChsFullDate(start_time) + ' ' + getChsDay(start_time) + ' ' + getTimeStr(start_time) + ' - ';
    if (isSameDay(start_time, end_time)) {
        result += getTimeStr(end_time);
    } else if (isSameMonth(start_time, end_time)) {
        result += getChsDate(end_time) + ' ' + getChsDay(end_time) + ' ' + getTimeStr(end_time);
    } else if (isSameYear(start_time, end_time)) {
        result += getChsMonthDay(end_time) + ' ' + getChsDay(end_time) + ' ' + getTimeStr(end_time);
    } else {
        result += getChsFullDate(end_time) + ' ' + getChsDay(end_time) + ' ' + getTimeStr(end_time);
    }
    return result;
}

function getTd(para) {
    return $('<td class="td-' + para + '"></td>');
}

var tdMap = {
    'status': 'status',
    'name': 'text',
    'description': 'text',
    'activity_time': 'time',
    'place': 'text',
    'book_time': 'time',
    'detail_url': 'editlink',
    'delete': 'deletelink'
}, tdActionMap = {
    'status': function(act, key) {
        return getSmartStatus(act);
    },
    'text': function(act, key) {
        return act[key];
    },
    'time': function(act, key) {
        return smartTimeMap[key](act);
    },
    'editlink': function(act, key) {
        return '<a href="' + act[key] + '"><span class="glyphicon glyphicon-pencil"></span> 详情</a>';
    },
    'deletelink':function(act, key) {
        return '<a href="#" id="'+act[key]+'" onclick="deleteact('+act[key]+')"><span class="glyphicon glyphicon-trash"></span></a>';
    }
}, smartTimeMap = {
    'activity_time': function(act) {
        return getSmartTimeRange(act.start_time, act.end_time);
    },
    'book_time': function(act) {
        return getSmartTimeRange(act.book_start, act.book_end);
    }
};

function deleteact(actid){
    //alert(actid);
    var i, len, curact;
    for(i = 0, len = activities.length; i < len; ++i){
        if(activities[i].delete == actid){
            curact = activities[i];
            break;
        }
    }
    var content = '确认删除<span style="color:red">'+getSmartStatus(curact)+'</span>活动：<span style="color:red">'+curact.name+'</span>？';
    $('#modalcontent').html(content);
    $('#'+actid).css("background-color","#FFE4C4");
    $('#deleteid').val(actid);
    $('#delModal').modal({
      keyboard: false,
      backdrop:false
    });
}

function delConfirm(){
    var delid = $('#deleteid').val();
    //alert(delid);
    var tmp  ="/adminpage/delete/";
    $.post(tmp,{'activityId':delid}, function(ret) {

    });
    $('#'+delid).css("background-color","#FFF");
    window.location.href="/adminpage/list/"
}

function delCancel(){
    var delid = $('#deleteid').val();
    $('#'+delid).css("background-color","#FFF");
}

function appendAct(act) {
    var tr = $('<tr id='+act.delete+'></tr>'), key;
    for (key in tdMap) {
        getTd(key).html(tdActionMap[tdMap[key]](act, key)).appendTo(tr);
    }
    $('#tbody-activities').append(tr);
}

function initialActs() {
    var i, len;
    for (i = 0, len = activities.length; i < len; ++i) {
        appendAct(activities[i]);
    }
}

clearActs();
initialActs();