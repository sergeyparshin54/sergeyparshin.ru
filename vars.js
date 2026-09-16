/* shared variant switcher A-J */
(function(){
  const v=document.getElementById('vars'); if(!v) return;
  const pages=[['A','index.html'],['B','b.html'],['C','c.html'],['D','d.html'],['E','e.html'],['F','f.html'],['G','g.html'],['H','h.html'],['I','i.html'],['J','j.html'],['K','k.html'],['L','l.html'],['M','m.html']];
  const cur=(location.pathname.split('/').pop()||'index.html');
  v.innerHTML=pages.map(([l,f])=>`<a href="${f}" class="${f===cur?'on':''}">${l}</a>`).join('');
})();
