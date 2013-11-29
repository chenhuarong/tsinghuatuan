/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-11-29
 * Time: 下午5:27
 */

var xmlhttp = null;

function clearHelp(groupid, helpid) {
    document.getElementById(groupid).setAttribute('class', 'form-group');
    document.getElementById(helpid).setAttribute('hidden', 'hidden');
}

function clearAllHelps() {
    clearHelp('usernameGroup', 'helpUsername');
    clearHelp('passwordGroup', 'helpPassword');
    clearHelp('submitGroup', 'helpSubmit');
}

function showSuccess(groupid, helpid) {
    document.getElementById(groupid).setAttribute('class', 'form-group has-success');
    document.getElementById(helpid).setAttribute('hidden', 'hidden');
}

function showError(groupid, helpid, text) {
    var dom = document.getElementById(helpid);
    dom.innerText = text;
    dom.removeAttribute('hidden');
    document.getElementById(groupid).setAttribute('class', 'form-group has-error');
}

function readyStateChanged() {
    if (xmlhttp.readyState==4)
    {// 4 = "loaded"
        if (xmlhttp.status==200)
        {// 200 = OK
            var result = xmlhttp.responseText;
            clearAllHelps();
            switch (result)
            {
                case 'Accepted':
                    document.getElementById('validationHolder').setAttribute('hidden', 'hidden');
                    document.getElementById('successHolder').removeAttribute('hidden');
                    break;

                case 'Rejected':
                    showError('passwordGroup', 'helpPassword', '密码错误！请输入info登录密码。');
                    break;

                case 'Error':
                    showError('submitGroup', 'helpSubmit', '出现了奇怪的错误，我们已经记录下来了，请稍后重试。')
                    break;
            }
        }
        else
        {
            showError('submitGroup', 'helpSubmit', '服务器连接异常，请稍后重试。')
        }
    }
}

function submitValidation(openid) {
    var form = document.getElementById('validationForm'),
        elems = form.elements,
        url = form.action,
        params = "openid=" + encodeURIComponent(openid),
        i, len;
    for (i = 0, len = elems.length; i < len; ++i) {
        params += '&' + elems[i].name + '=' + encodeURIComponent(elems[i].value);
    }
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open('POST', url, true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = readyStateChanged;
    xmlhttp.send(params);
    return false;
}

window.setupWeixin({'optionMenu':false, 'toolbar':false});

clearAllHelps();