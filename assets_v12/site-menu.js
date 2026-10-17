/* Shared accessible drawer for navigation and services */
(function(){
"use strict";
function init(){
  var trigger=document.querySelector("[data-site-menu-open]");
  var drawer=document.getElementById("site-menu-dialog");
  var backdrop=document.querySelector("[data-site-menu-backdrop]");
  if(!trigger||!drawer||!backdrop)return;
  var closeButton=drawer.querySelector("[data-site-menu-close]");
  var wasFocused=null;
  function close(restore){
    if(drawer.hidden)return;
    drawer.hidden=true;
    backdrop.hidden=true;
    trigger.setAttribute("aria-expanded","false");
    trigger.setAttribute("aria-label","Открыть меню");
    document.documentElement.classList.remove("site-menu-open");
    if(restore&&wasFocused&&typeof wasFocused.focus==="function")wasFocused.focus();
  }
  function open(){
    if(!drawer.hidden)return;
    wasFocused=document.activeElement;
    drawer.hidden=false;
    backdrop.hidden=false;
    trigger.setAttribute("aria-expanded","true");
    trigger.setAttribute("aria-label","Закрыть меню");
    document.documentElement.classList.add("site-menu-open");
    closeButton.focus();
  }
  trigger.addEventListener("click",function(){if(drawer.hidden)open();else close(true)});
  closeButton.addEventListener("click",function(){close(true)});
  backdrop.addEventListener("click",function(){close(true)});
  drawer.addEventListener("click",function(e){
    var link=e.target.closest("a");
    if(link){close(false);}
  });
  document.addEventListener("keydown",function(e){
    if(drawer.hidden)return;
    if(e.key==="Escape"){e.preventDefault();close(true);return;}
    if(e.key==="Tab"){
      var focusables=Array.from(drawer.querySelectorAll('a[href],button:not([disabled])')).filter(function(x){return x.getClientRects().length>0});
      if(!focusables.length)return;
      var first=focusables[0],last=focusables[focusables.length-1];
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
    }
  });
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();