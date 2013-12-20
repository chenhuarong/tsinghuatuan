/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-12-11
 * Time: 下午6:47
 */

var current_screen = 'welcome',
    screens = {
        'welcome': function() {
            // do nothing.
        },
        'checkin': function() {
            setTimeout($('#input-uid').focus());
        }
    },
    tickets_count = 0;

function setFullScreen() {
    if (screenfull.enabled) {
        screenfull.request();
    }
}

function hide_all_screens(){
    var i;
    for (i in screens) {
        $('#' + i + '-screen').hide();
    }
}

function auto_adjust() {
    if ($(window).data('fullscreen-state')) {
        $(document.body).height(screen.height);
    } else {
        $(document.body).removeAttr('style');
    }
    $(document.body).width(screen.width);
    hide_all_screens();
    $('#' + current_screen + '-screen').show();
    screens[current_screen]();
}

document.addEventListener(screenfull.raw.fullscreenchange, function() {
    if (screenfull.isFullscreen) {
        current_screen = 'checkin';
    } else {
        current_screen = 'welcome';
    }
    auto_adjust();
});

function enter_checkin() {
    setFullScreen();
}

var ticket_result_img_map = {
    'success': 'good.png',
    'error': 'error.png',
    'warning': 'warning.png'
    }, ticket_result_class_map = {
    'success': 'success',
    'error': 'danger',
    'warning': 'warning'
    }, ticket_msg_map = {
    'unknown': '未知错误',
    'noact': '请刷新',
    'rejected': '无效票',
    'nouser': '未注册用户',
    'used': '已使用',
    'accepted': '检票成功',
    'noticket': '没有票'
}, MAX_TICKET_COUNT = 5;

function append_tickets_table(uid) {
    if (tickets_count >= MAX_TICKET_COUNT) {
        $('#tickets-table-body tr:last-child').remove();
    }
    ++tickets_count;
    $('#tickets-table-body').prepend('<tr class="warning"><td class="ticket-no">' + tickets_count + '</td><td class="ticket-status"><img class="ticket-status-img" src="/static/img/checking.gif"></td><td class="ticket-uid">' + uid + '</td><td class="ticket-stuid"></td><td class="ticket-time">' + new Date().toLocaleTimeString() + '</td><td class="ticket-msg"></td>');
}

function update_tickets_table(data) {
    var dom = $('#tickets-table-body tr:first-child'), c = dom.children();
    dom.attr('class', ticket_result_class_map[data.result]);
    $(c[1]).children().attr('src', '/static/img/' + ticket_result_img_map[data.result]);
    $(c[3]).text(data.stuid);
    $(c[4]).text(new Date().toLocaleTimeString());
    $(c[5]).text(data.msg in ticket_msg_map ? ticket_msg_map[data.msg] : data.msg);
}

function beforeSubmit(formData, jqForm, options) {
    return true;
}

function submitResponse(data) {
    update_tickets_table(data);
}

function submitError(xhr) {
    update_tickets_table({
        'result': 'error',
        'stuid': 'Unknown',
        'msg': xhr.status + ' ' + xhr.statusText
    });
}

function submitComplete(xhr) {
    $('#input-uid').val('').prop('readonly', false).focus();
}

$('#checkin-form').submit(function() {
    $('#input-uid').prop('readonly', true);
    append_tickets_table($('#input-uid').val());
    var options = {
        dataType: 'json',
        beforeSubmit: beforeSubmit,
        success: submitResponse,
        error: submitError,
        complete: submitComplete
    };
    $(this).ajaxSubmit(options);
    return false;
});
