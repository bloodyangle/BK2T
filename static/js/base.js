//监听div大小变化
(function($, h, c) {
   var a = $([]),
   e = $.resize = $.extend($.resize, {}),
   i,
   k = "setTimeout",
   j = "resize",
   d = j + "-special-event",
   b = "delay",
   f = "throttleWindow";
   e[b] = 250;
   e[f] = true;
   $.event.special[j] = {
      setup: function() {
         if (!e[f] && this[k]) {
            return false;
         }
         var l = $(this);
         a = a.add(l);
         $.data(this, d, {
            w: l.width(),
            h: l.height()
         });
         if (a.length === 1) {
            g();
         }
      },
      teardown: function() {
         if (!e[f] && this[k]) {
            return false;
         }
         var l = $(this);
         a = a.not(l);
         l.removeData(d);
         if (!a.length) {
            clearTimeout(i);
         }
      },
      add: function(l) {
         if (!e[f] && this[k]) {
            return false;
         }
         var n;
         function m(s, o, p) {
            var q = $(this),
            r = $.data(this, d);
            r.w = o !== c ? o: q.width();
            r.h = p !== c ? p: q.height();
            n.apply(this, arguments);
         }
         if ($.isFunction(l)) {
            n = l;
            return m;
         } else {
            n = l.handler;
            l.handler = m;
         }
      }
   };
   function g() {
      i = h[k](function() {
         a.each(function() {
            var n = $(this),
            m = n.width(),
            l = n.height(),
            o = $.data(this, d);
            if (m !== o.w || l !== o.h) {
               n.trigger(j, [o.w = m, o.h = l]);
            }
         });
         g();
      },
      e[b]);
   }
})(jQuery, this);
//封装id
function createKeyIDObj(keyID){
    return {
        id:keyID
    }
}
//根据key匹配id  加入数据
function adddata(ids,res){
    $("#" + ids).html(res)
}
//根据key匹配id,加入数据到表单
function addInputData(ids,res){
    $("#" + ids).val(res)
    $(".FilterCheckbox").each(function(){
        if($(this).val() == 'false'){
            $(this).prop("checked",false)
        }else if($(this).val() == 'true'){
            $(this).prop("checked",true)
        }
    })
}
//获取页面传参
function getUrlParam(name) {
  var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
  var r = decodeURI(window.location.search).substr(1).match(reg); //匹配目标参数
  if (r != null) return unescape(r[2]); return null; //返回参数值
}
//给主页的tabs增加选项页
function addParentTab(title,url,index){
    parent.nthTabs.addTab({
        id:index,
        title:title,
        content:'<iframe class="page-iframe" src="'+ url +'" frameborder="no" border="no" height="100%" width="100%"></iframe>',
    })
    parent.nthTabs.setActTab(index)
    parent.nthTabs.locationTab()
}
//时间格式转换
function Appendzero(obj){
    if(obj < 10){
        return "0" + obj
    }else{
        return obj
    }
}
function myformatter(date){
    var y = date.getFullYear();
    var m = date.getMonth()+1;
    var d = date.getDate();
    var h = date.getHours()
    var minutes = date.getMinutes()
    var s = date.getSeconds()
    return Appendzero(y) + '-' + Appendzero(m) + '-' + Appendzero(d) + ' ' + Appendzero(h) + ':' + Appendzero(minutes);
}
function myTimeformatter(date){
    var y = date.getFullYear();
    var m = date.getMonth()+1;
    var d = date.getDate();
    var h = date.getHours()
    var minutes = date.getMinutes()
    var s = date.getSeconds()
    return Appendzero(y) + '-' + Appendzero(m) + '-' + Appendzero(d) + ' ' + Appendzero(h) + ':' + Appendzero(minutes) + ':' + Appendzero(s);
}
