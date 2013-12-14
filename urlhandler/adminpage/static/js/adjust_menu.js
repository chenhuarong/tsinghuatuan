/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-12-14
 * Time: 上午11:36
 */

var menus = null;

var containers = ['loading', 'result', 'main'];

function hide_all_containers() {
    var i;
    for (i in containers) {
        $('#container-' + containers[i]).hide();
    }
}

function show_container(name) {
    hide_all_containers();
    $('#container-' + name).show();
}

function show_loading(msg) {
    $('#loading-msg').text(msg);
    show_container('loading');
}

function show_result(msg) {
    $('#result-msg').text(msg);
    show_container('result');
}

function show_main() {
    show_container('main');
}

function get_custom_menu(url) {
    $.ajax({
        url: url,
        complete: function(xhr, ts) {
        },
        dataType: 'json',
        error: function(xhr, errmsg, e) {
        },
        success: function(jsonData) {
            menus = jsonData;
            update_menus(menus);
            update_alters(alters);
            show_main();
        }
    })
}

var htmls = {
    'up-icon': '<span class="glyphicon glyphicon-circle-arrow-up"></span>',
    'down-icon': '<span class="glyphicon glyphicon-circle-arrow-down"></span>',
    'minus-icon': '<span class="glyphicon glyphicon-minus"></span>',
    'plus-icon': '<span class="glyphicon glyphicon-plus"></span>',
    'empty-icon': '<span class="glyphicon"></span>'
}

function upmenu(count) {
    if (count > 0) {
        var menu = menus[count];
        menus[count] = menus[count - 1];
        menus[count - 1] = menu;
        update_menus(menus);
     }
}

function downmenu(count) {
    var len = menus.length;
    if (count < len - 1) {
        var menu = menus[count];
        menus[count] = menus[count + 1];
        menus[count + 1] = menu;
        update_menus(menus);
    }
}

function wrap_menu_item_html(menu, i, len) {
    return '<li class="list-group-item">'
        + '<button class="btn btn-link"'
        + (i > 0 ? ('onclick="upmenu(' + i + ')"') : 'disabled')
        + '>'
        + (i > 0 ? htmls['up-icon'] : htmls['empty-icon'])
        + '</button>'
        + '<button class="btn btn-link"'
        + (i < len - 1 ? ('onclick="downmenu(' + i + ')"') : 'disabled')
        + '>'
        + (i < len - 1 ? htmls['down-icon'] : htmls['empty-icon'])
        + '</button>'
        + menu.name
        + '</li>';
}

function wrap_alter_item_html(alter, i) {
    var isFull = (menus == null ? false : (menus.length == 5));
    return '<li class="list-group-item">'
        + '<button class="btn btn-link"'
        + (isFull ? 'disabled' : 'onclick="change_alter(' + i + ')"')
        + '>'
        + (alters[i].inmenu ? htmls['minus-icon'] : htmls['plus-icon'])
        + '</button>'
        + alter.name
        + '</li>';
}

function update_menus(menus) {
    var i, str = '', len = menus.length;
    for (i in menus) {
        str += wrap_menu_item_html(menus[i], i, len);
    }
    $('#current-menus').html(str);
}

function update_alters(alters) {
    update_alters_status(menus, alters);
    var i, str = '';
    for (i in alters) {
        str += wrap_alter_item_html(alters[i], i);
    }
    $('#current-alters').html(str);
}

function update_alters_status(menus, alters) {
    var i, j;
    for (i in menus) {
        for (j in alters) {
            if (alters[j].id == menus[i].id) {
                alters[j]['inmenu'] = true;
                break;
            }
        }
    }
}

function change_alter(i) {
    if (alters[i].inmenu) {
        var j;
        for (j in menus) {
            if (menus[j].id == alters[i].id) {
                menus.splice(j, 1);
                break;
            }
        }
        alters[i].inmenu = false;
    } else {
        menus.push(alters[i]);
    }
    update_menus(menus);
    update_alters(alters);
}

update_alters(alters);


function beforeSubmit(formData, jqForm, options) {
    formData.push({
        'name': 'menus',
        'required': false,
        'type': 'text',
        'value': JSON.stringify(menus)
    });
    return true;
}

function submitResponse(data) {

}

function submitError(xhr) {

}

function submitComplete(xhr) {
    show_result(xhr.responseText);
}

$('#submit-weixin-menu-form').submit(function() {
    show_loading('正在提交...');
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