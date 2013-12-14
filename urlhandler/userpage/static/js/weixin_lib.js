/**
 * Created with PyCharm.
 * User: Epsirom
 * Date: 13-11-29
 * Time: 上午8:49
 */

/* setting is a dict-like object.
 * every value is boolean.
 * setting.optionMenu true means show.
 * setting.toolbar true means show.
 */
window.setupWeixin = function(setting) {
    if (setting.optionMenu !== undefined) {
        // http://mp.weixin.qq.com/wiki/index.php?title=%E9%9A%90%E8%97%8F%E5%BE%AE%E4%BF%A1%E4%B8%AD%E7%BD%91%E9%A1%B5%E5%8F%B3%E4%B8%8A%E8%A7%92%E6%8C%89%E9%92%AE
        document.addEventListener('WeixinJSBridgeReady', function onBridgeReady() {
            WeixinJSBridge.call(setting.optionMenu ? 'showOptionMenu' : 'hideOptionMenu');
        })
    }
    if (setting.toolbar !== undefined) {
        // http://mp.weixin.qq.com/wiki/index.php?title=%E9%9A%90%E8%97%8F%E5%BE%AE%E4%BF%A1%E4%B8%AD%E7%BD%91%E9%A1%B5%E5%BA%95%E9%83%A8%E5%AF%BC%E8%88%AA%E6%A0%8F
        document.addEventListener('WeixinJSBridgeReady', function onBridgeReady() {
            WeixinJSBridge.call(setting.toolbar ? 'showToolbar' : 'hideToolbar');
        });
    }
}

/*
 * return: network_type:wifi wifi网络
 * * network_type:edge 非wifi,包含3G/2G
 * * network_type:fail 网络断开连接
 * * network_type:wwan（2g或者3g）
 */
// http://mp.weixin.qq.com/wiki/index.php?title=%E7%BD%91%E9%A1%B5%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E7%BD%91%E7%BB%9C%E7%8A%B6%E6%80%81
window.getNetworkStatus = function() {
    if (WeixinJSBridge) {
        return WeixinJSBridge.invoke('getNetworkType',{},
            function(e){
                WeixinJSBridge.log(e.err_msg);
            });
    }
}

function setfooter(){
    //正文高度
    var docHeight = document.body.offsetHeight;
    //可见页面高度
    var winHeight = document.documentElement.clientHeight;
    var footer = document.getElementById('footer');
    if(docHeight+80 > winHeight){
        footer.style.position = "static";
    }
    else{
        footer.style.position = "absolute";
    }
}

function doResize(){
    setfooter();
}

window.onresize = function(){
    doResize();
}

window.onload = function() {
    doResize();
}