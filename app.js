let allItems=[];let activeFilter='all';
const stageNames={20:'Preparación',30:'Comité',40:'Consulta',50:'Aprobación',60:'Publicación',90:'Revisión',95:'Retirada'};
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const fmtDate=s=>{if(!s)return '—';const d=new Date(s+'T12:00:00');return isNaN(d)?s:new Intl.DateTimeFormat('es',{day:'2-digit',month:'short',year:'numeric'}).format(d)};
function bucket(item){const n=parseInt(item.stage||0,10);if(n===90||n===95)return'review';if(n>=60)return'published';return'development'}
function badge(item){const b=bucket(item);return b==='published'?['Publicada','pub']:b==='review'?['Revisión','rev']:['En desarrollo','dev']}
function render(){
 const q=$('#searchInput').value.trim().toLowerCase();
 const items=allItems.filter(x=>(activeFilter==='all'||bucket(x)===activeFilter)&&(!q||[x.reference,x.topic,x.title,x.description,x.stage].join(' ').toLowerCase().includes(q)));
 $('#cards').innerHTML=items.map(x=>{const [label,cls]=badge(x);const major=parseInt(x.stage||0,10);return `
 <article class="card">
  <div class="card-top"><div class="ref">${esc(x.reference)}</div><span class="badge ${cls}">${label}</span></div>
  <div class="topic">${esc(x.topic)}</div>
  <div class="title">${esc(x.title)}</div>
  <div class="meta">
   <div><small>Etapa ISO</small><b>${esc(x.stage||'—')} · ${esc(stageNames[major]||'')}</b></div>
   <div><small>Último cambio</small><b>${fmtDate(x.pubDate)}</b></div>
  </div>
  <p class="desc">${esc(x.description||'Actualización disponible en ISO.org.')}</p>
  <div class="card-actions"><span><i class="source-dot"></i>RSS oficial</span><a href="${esc(x.link)}" target="_blank" rel="noopener">Ver en ISO ↗</a></div>
 </article>`}).join('')||'';
 $('#emptyState').hidden=items.length>0;
}
function renderSources(feeds){
 $('#sourceList').innerHTML=feeds.map(f=>`<div class="source-row"><b>${esc(f.reference)}</b><a href="${esc(f.page)}" target="_blank" rel="noopener">ISO.org ↗</a></div>`).join('');
}
function stats(){
 $('#countTotal').textContent=allItems.length;
 $('#countDev').textContent=allItems.filter(x=>bucket(x)==='development').length;
 $('#countPub').textContent=allItems.filter(x=>bucket(x)==='published').length;
 $('#countReview').textContent=allItems.filter(x=>bucket(x)==='review').length;
}
async function init(){
 try{
  const [d,f]=await Promise.all([fetch('data/updates.json?ts='+Date.now()).then(r=>r.json()),fetch('data/feeds.json').then(r=>r.json())]);
  allItems=(d.items||[]).sort((a,b)=>(b.pubDate||'').localeCompare(a.pubDate||''));
  $('#lastUpdate').textContent='Datos actualizados: '+new Intl.DateTimeFormat('es',{dateStyle:'medium',timeStyle:'short'}).format(new Date(d.generated_at));
  stats();render();renderSources(f.feeds||[]);
 }catch(e){$('#cards').innerHTML='<div class="loading-card">No se pudieron cargar los datos. Intenta nuevamente en unos minutos.</div>';$('#lastUpdate').textContent='Actualización temporalmente no disponible';}
}
$('#searchInput').addEventListener('input',render);
document.querySelectorAll('.chip').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));b.classList.add('active');activeFilter=b.dataset.filter;render()}));
init();