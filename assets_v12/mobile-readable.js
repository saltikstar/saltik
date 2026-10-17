/* Accessible one-card mobile carousels. No automatic movement, no hidden text. */
(function(){
"use strict";
var screen=window.matchMedia("(max-width:720px)");
function init(){
  document.querySelectorAll("[data-compact-carousel]").forEach(function(scroller){
    if(scroller.dataset.carouselReady==="1")return;
    var cards=Array.from(scroller.children);
    if(cards.length<2)return;
    scroller.dataset.carouselReady="1";
    var toolbar=document.createElement("div");
    toolbar.className="readable-carousel-toolbar";
    toolbar.innerHTML='<span class="readable-carousel-hint">Листайте карточки</span><span class="readable-carousel-actions"><button type="button" class="readable-carousel-button" aria-label="Предыдущая карточка">‹</button><span class="readable-carousel-count" aria-live="polite">1 / '+cards.length+'</span><button type="button" class="readable-carousel-button" aria-label="Следующая карточка">›</button></span>';
    scroller.parentNode.insertBefore(toolbar,scroller);
    var buttons=toolbar.querySelectorAll("button"),count=toolbar.querySelector(".readable-carousel-count");
    function index(){
      var current=0,closest=Infinity;
      cards.forEach(function(el,i){
        var d=Math.abs(el.offsetLeft-cards[0].offsetLeft-scroller.scrollLeft);
        if(d<closest){closest=d;current=i}
      });
      return current;
    }
    function update(){
      var active=index();
      count.textContent=(active+1)+" / "+cards.length;
      buttons[0].disabled=active===0;
      buttons[1].disabled=active===cards.length-1;
      if(screen.matches){
        scroller.setAttribute("role","region");
        scroller.setAttribute("aria-label",scroller.getAttribute("data-compact-label")||"Карточки");
        scroller.setAttribute("tabindex","0");
      }else{
        scroller.removeAttribute("role");scroller.removeAttribute("aria-label");scroller.removeAttribute("tabindex");
      }
    }
    function go(n){
      var target=Math.max(0,Math.min(cards.length-1,index()+n));
      scroller.scrollTo({left:cards[target].offsetLeft-cards[0].offsetLeft,behavior:window.matchMedia("(prefers-reduced-motion:reduce)").matches?"auto":"smooth"});
    }
    buttons[0].addEventListener("click",function(){go(-1)});
    buttons[1].addEventListener("click",function(){go(1)});
    scroller.addEventListener("scroll",update,{passive:true});
    scroller.addEventListener("keydown",function(e){if(!screen.matches)return;if(e.target!==scroller)return;if(e.key==="ArrowRight"){e.preventDefault();go(1)}else if(e.key==="ArrowLeft"){e.preventDefault();go(-1)}});
    window.addEventListener("resize",update,{passive:true});
    if(screen.addEventListener)screen.addEventListener("change",update);
    update();
  });
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
