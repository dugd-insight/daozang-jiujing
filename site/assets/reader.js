function onReady(fn){ if(document.readyState!=='loading'){fn();}else{document.addEventListener('DOMContentLoaded',fn);} }
var __deb = function(fn, ms){ var t; return function(){ clearTimeout(t); t = setTimeout(fn, ms); }; };
onReady(function(){
  var book = document.body.getAttribute('data-book');
  var simp = localStorage.getItem('gj-simp') !== '0';
  var showNotes = localStorage.getItem('gj-notes') !== '0';
  var dark = localStorage.getItem('gj-theme') === 'dark';
  function apply(){
    document.body.setAttribute('data-theme', dark ? 'dark' : 'light');
    document.body.classList.toggle('trad', !simp);
    document.body.classList.toggle('no-notes', !showNotes);
    var bt = document.getElementById('btnTg');
    var bn = document.getElementById('btnNotes');
    var th = document.getElementById('btnTheme');
    if(bt) bt.textContent = simp ? '切换到繁体原文' : '切换到简体正文';
    if(bn){ bn.textContent = showNotes ? '隐藏注解' : '显示注解'; bn.classList.toggle('on', !showNotes); }
    if(th) th.textContent = dark ? '☀️' : '🌙';
  }
  var bt = document.getElementById('btnTg');
  if(bt) bt.onclick = function(){ simp = !simp; localStorage.setItem('gj-simp', simp ? '1' : '0'); apply(); };
  var bn = document.getElementById('btnNotes');
  if(bn) bn.onclick = function(){ showNotes = !showNotes; localStorage.setItem('gj-notes', showNotes ? '1' : '0'); apply(); };
  var th = document.getElementById('btnTheme');
  if(th) th.onclick = function(){ dark = !dark; localStorage.setItem('gj-theme', dark ? 'dark' : 'light'); apply(); };
  apply();

  if(!book) return;
  var ch = parseInt(document.body.getAttribute('data-ch') || '0', 10);
  var pg = parseInt(document.body.getAttribute('data-pg') || '0', 10);
  if(ch > 0 && pg > 0){
    localStorage.setItem(book + '-pos', JSON.stringify({ch: ch, pg: pg}));
    try{
      var vis = JSON.parse(localStorage.getItem(book + '-visited') || '[]');
      if(vis.indexOf(ch) < 0){ vis.push(ch); localStorage.setItem(book + '-visited', JSON.stringify(vis)); }
    }catch(e){}
    var skey = book + '-s-' + ch + '-' + pg;
    var sp = parseInt(localStorage.getItem(skey) || '0', 10);
    if(sp > 0) requestAnimationFrame(function(){ window.scrollTo(0, sp); });
    var saveScroll = __deb(function(){ try{ localStorage.setItem(skey, String(window.scrollY)); }catch(e){} }, 250);
    window.addEventListener('scroll', saveScroll);
    window.addEventListener('beforeunload', saveScroll);
  }
  var box = document.getElementById('continueBox');
  if(box){
    try{
      var pos = JSON.parse(localStorage.getItem(book + '-pos') || 'null');
      if(pos && pos.ch){
        var link = document.getElementById('continueLink');
        if(link) link.href = 'c' + ('0' + pos.ch).slice(-2) + '_' + ('0' + pos.pg).slice(-2) + '.html';
        var lb = document.getElementById('continueLabel');
        if(lb) lb.textContent = '第' + pos.ch + '章 · 第' + pos.pg + '页';
        box.style.display = 'block';
      }
    }catch(e){}
    try{
      var vis = JSON.parse(localStorage.getItem(book + '-visited') || '[]');
      var items = document.querySelectorAll('.toclist li[data-ch]');
      for(var i = 0; i < items.length; i++){
        var n = parseInt(items[i].getAttribute('data-ch'), 10);
        if(vis.indexOf(n) >= 0){ items[i].classList.add('read'); }
      }
    }catch(e){}
  }
});
