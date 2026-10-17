/* Плавная мобильная карусель: работает касанием и с кнопками. Без внешних библиотек. */
(function(){
"use strict";
var mq=window.matchMedia("(max-width:700px)");
var arrow='<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>';
var items=[];
function visible(el){return el&&el.getClientRects().length>0}
function activeIndex(el,cards){
var x=el.scrollLeft;
var nearest=0,dist=Infinity;
cards.forEach(function(card,i){var d=Math.abs(card.offsetLeft-cards[0].offsetLeft-x);if(d<dist){nearest=i;dist=d}});
return nearest;
}
function init(){
document.querySelectorAll("[data-mobile-slider]").forEach(function(el){
if(el.dataset.mobileSliderReady)return;
var cards=Array.from(el.children).filter(function(n){return n.nodeType===1});
if(cards.length<2)return;
el.dataset.mobileSliderReady="1";
el.setAttribute("role","region");
el.setAttribute("aria-roledescription","карусель");
el.setAttribute("aria-label",el.getAttribute("data-mobile-title")||"Карточки");
el.setAttribute("tabindex","0");
var toolbar=document.createElement("div");
toolbar.className="mobile-slider-toolbar";
toolbar.innerHTML='<span class="mobile-slider-hint"><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 12h10m-4-4 4 4-4 4M6 19V5"/></svg>Листайте</span><span class="mobile-slider-controls"><button type="button" class="mobile-slider-button mobile-slider-prev" aria-label="Предыдущая карточка">'+arrow+'</button><span class="mobile-slider-count" aria-live="off">1 / '+cards.length+'</span><button type="button" class="mobile-slider-button mobile-slider-next" aria-label="Следующая карточка">'+arrow+'</button></span>';
el.parentNode.insertBefore(toolbar,el);
var previous=toolbar.querySelector(".mobile-slider-prev");
var next=toolbar.querySelector(".mobile-slider-next");
next.querySelector("svg").style.transform="rotate(180deg)";
var count=toolbar.querySelector(".mobile-slider-count");
function update(){
if(!mq.matches)return;
var idx=activeIndex(el,cards);
count.textContent=(idx+1)+" / "+cards.length;
previous.disabled=(idx===0);
next.disabled=(idx===cards.length-1);
}
function move(step){
var idx=activeIndex(el,cards);
var to=Math.min(cards.length-1,Math.max(0,idx+step));
el.scrollTo({left:cards[to].offsetLeft-cards[0].offsetLeft,behavior:window.matchMedia("(prefers-reduced-motion:reduce)").matches?"auto":"smooth"});
}
previous.addEventListener("click",function(){move(-1)});
next.addEventListener("click",function(){move(1)});
el.addEventListener("keydown",function(ev){if(!mq.matches)return;if(ev.key==="ArrowLeft"){ev.preventDefault();move(-1)}if(ev.key==="ArrowRight"){ev.preventDefault();move(1)}});
el.addEventListener("scroll",update,{passive:true});
window.addEventListener("resize",update,{passive:true});
if(mq.addEventListener)mq.addEventListener("change",update);
update();
items.push({el:el,update:update});
});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
