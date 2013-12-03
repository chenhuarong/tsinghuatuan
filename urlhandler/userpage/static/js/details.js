/**
 * Created with PyCharm.
 * User: LY
 * Date: 13-12-1
 * Time: 下午11:00
 * To change this template use File | Settings | File Templates.
 */

document.getElementById('slidedown').onclick = function(){
        document.getElementById('actabstract').style.display = "none";
        document.getElementById('actdetails').style.display = "block";

}
document.getElementById('slideup').onclick = function(){
        document.getElementById('actabstract').style.display = "block";
        document.getElementById('actdetails').style.display = "none";
}

 function copyClip(){
    var textcopy = document.getElementById('actkey').innerHTML;
    if(navigator.userAgent.toLowerCase().indexOf('ie') > -1) {
        clipboardData.setData('Text',textcopy);
        alert ("该地址已复制到剪切板！");
    } else {
        prompt("请复制以下代码:",textcopy);
    }
}

document.getElementById('copykey').onclick = function(){
    copyClip();
}