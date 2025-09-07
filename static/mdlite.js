function mdLite(s){
  if (!s) return "";
  s = String(s);
  // basic escape
  s = s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  // **bold**
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // *italic*
  s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // newlines -> <br>
  s = s.replace(/\n/g, '<br>');
  return s;
}

function showDialog(msg){
  const d = document.createElement('div');
  d.className='dialog';
  d.innerHTML = '<div class="box">'+ mdLite(msg) +'</div>';
  d.addEventListener('click', ()=> document.body.removeChild(d));
  document.body.appendChild(d);
}

let toastTimer = null;
function toast(msg){
  const t = document.createElement('div');
  t.className='toast';
  t.innerHTML = mdLite(msg);
  document.body.appendChild(t);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>{
    if (t.parentNode) t.parentNode.removeChild(t);
  }, 2000);
}
