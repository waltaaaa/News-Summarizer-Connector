"""Render the article-keyword graph as a self-contained interactive HTML file.

Nodes: keyword hubs (sized by article count) + processed articles.
Edges: article -> keyword. No external dependencies; open output/graph.html
in any browser. Regenerate after each processing run.
"""
import json
import os

import common

OUT_PATH = os.path.join(common.REPO_ROOT, "output", "graph.html")

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>News Summarizer — Knowledge Graph</title>
<style>
  html,body{margin:0;height:100%;background:#11131a;color:#dde;font-family:Segoe UI,system-ui,sans-serif;overflow:hidden}
  #c{display:block;cursor:grab}
  #hud{position:fixed;top:10px;left:12px;background:rgba(20,22,32,.88);padding:10px 14px;border-radius:10px;
       font-size:13px;max-width:330px;line-height:1.5;border:1px solid #2a2e40}
  #hud h1{font-size:15px;margin:0 0 4px}
  #info{position:fixed;bottom:10px;left:12px;right:12px;background:rgba(20,22,32,.92);padding:10px 14px;
        border-radius:10px;font-size:13px;display:none;border:1px solid #2a2e40;max-height:30%;overflow:auto}
  #search{width:100%;margin-top:6px;background:#1b1e2b;border:1px solid #333a52;color:#dde;
          border-radius:6px;padding:4px 8px;font-size:13px}
  .kw{color:#ffb35c}.art{color:#7fb4ff}.dim{color:#889}
  a{color:#9ecbff}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hud">
  <h1>News repository — knowledge graph</h1>
  <span class="kw">&#9679;</span> keywords (size = article count) &nbsp;
  <span class="art">&#9679;</span> articles<br>
  <span class="dim">Drag to pan &middot; scroll to zoom &middot; hover for titles &middot; click a node to inspect &amp; highlight</span>
  <input id="search" placeholder="search keywords &amp; headlines...">
</div>
<div id="info"></div>
<script>
const DATA = __DATA__;
const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
let W,H;function resize(){W=canvas.width=innerWidth;H=canvas.height=innerHeight}resize();addEventListener('resize',resize);
const nodes=DATA.nodes,links=DATA.links;
const byId={};nodes.forEach(n=>{byId[n.id]=n;n.x=(Math.random()-0.5)*900;n.y=(Math.random()-0.5)*700;n.vx=0;n.vy=0;
  n.r=n.t=='k'?5+Math.sqrt(n.c)*3.2:3.5;});
links.forEach(l=>{l.s=byId[l.source];l.t2=byId[l.target]});
const adj={};links.forEach(l=>{(adj[l.source]=adj[l.source]||[]).push(l.target);(adj[l.target]=adj[l.target]||[]).push(l.source)});
let cam={x:0,y:0,z:0.9},drag=null,dragNode=null,hover=null,selected=null,query='';
let alpha=1;
function tick(){
  if(alpha>0.005){
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const a=nodes[i],b=nodes[j];let dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+0.01;
      if(d2<90000){const f=900/d2;dx*=f;dy*=f;a.vx-=dx;a.vy-=dy;b.vx+=dx;b.vy+=dy;}}
    links.forEach(l=>{let dx=l.t2.x-l.s.x,dy=l.t2.y-l.s.y;const d=Math.sqrt(dx*dx+dy*dy)+0.01,f=(d-70)*0.02/d;
      dx*=f;dy*=f;l.s.vx+=dx;l.s.vy+=dy;l.t2.vx-=dx;l.t2.vy-=dy;});
    nodes.forEach(n=>{n.vx-=n.x*0.0015;n.vy-=n.y*0.0015;
      if(n!==dragNode){n.x+=n.vx*alpha;n.y+=n.vy*alpha;}n.vx*=0.6;n.vy*=0.6;});
    alpha*=0.998;
  }
  draw();requestAnimationFrame(tick);
}
function sx(n){return (n.x-cam.x)*cam.z+W/2}function sy(n){return (n.y-cam.y)*cam.z+H/2}
function matches(n){return query&&n.label.toLowerCase().includes(query)}
function draw(){
  ctx.clearRect(0,0,W,H);
  const focus=selected||hover;
  const nb=focus?new Set([focus.id,...(adj[focus.id]||[])]):null;
  ctx.lineWidth=1;
  links.forEach(l=>{
    const lit=nb&&(l.source==focus.id||l.target==focus.id);
    ctx.strokeStyle=lit?'rgba(255,200,120,0.85)':'rgba(120,130,170,0.18)';
    ctx.beginPath();ctx.moveTo(sx(l.s),sy(l.s));ctx.lineTo(sx(l.t2),sy(l.t2));ctx.stroke();});
  nodes.forEach(n=>{
    const x=sx(n),y=sy(n);if(x<-40||y<-40||x>W+40||y>H+40)return;
    let col=n.t=='k'?'#ffb35c':'#6ea8ff';
    if(nb&&!nb.has(n.id))col=n.t=='k'?'rgba(255,179,92,0.18)':'rgba(110,168,255,0.15)';
    if(matches(n))col='#7CFC9A';
    ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y,n.r*cam.z,0,7);ctx.fill();
    if(n.t=='k'&&cam.z>0.45||(nb&&nb.has(n.id))||matches(n)){
      ctx.fillStyle=nb&&!nb.has(n.id)?'rgba(200,200,220,0.25)':'#e8e8f2';
      ctx.font=(n.t=='k'?12:10)*Math.min(cam.z,1.4)+'px Segoe UI';
      ctx.fillText(n.label.slice(0,46),x+n.r*cam.z+3,y+3);}
  });
}
function pick(mx,my){let best=null,bd=144;nodes.forEach(n=>{const dx=sx(n)-mx,dy=sy(n)-my,d=dx*dx+dy*dy;
  if(d<bd+n.r*n.r*cam.z*cam.z&&d<((n.r*cam.z+7)**2)){best=n;bd=d}});return best}
canvas.onmousedown=e=>{const n=pick(e.clientX,e.clientY);if(n){dragNode=n;alpha=Math.max(alpha,0.3)}else drag={x:e.clientX,y:e.clientY};canvas.style.cursor='grabbing'};
addEventListener('mouseup',e=>{if(dragNode&&Math.abs(e.movementX)+Math.abs(e.movementY)<3){}drag=null;dragNode=null;canvas.style.cursor='grab'});
canvas.onmousemove=e=>{
  if(dragNode){dragNode.x=(e.clientX-W/2)/cam.z+cam.x;dragNode.y=(e.clientY-H/2)/cam.z+cam.y;alpha=Math.max(alpha,0.2);return}
  if(drag){cam.x-=(e.clientX-drag.x)/cam.z;cam.y-=(e.clientY-drag.y)/cam.z;drag={x:e.clientX,y:e.clientY};return}
  hover=pick(e.clientX,e.clientY);canvas.style.cursor=hover?'pointer':'grab';};
canvas.onclick=e=>{const n=pick(e.clientX,e.clientY);selected=n===selected?null:n;showInfo(selected)};
canvas.onwheel=e=>{e.preventDefault();const f=e.deltaY<0?1.12:0.89;cam.z=Math.min(4,Math.max(0.15,cam.z*f))};
document.getElementById('search').oninput=e=>{query=e.target.value.toLowerCase().trim()};
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function showInfo(n){
  const el=document.getElementById('info');
  if(!n){el.style.display='none';return}
  el.style.display='block';
  if(n.t=='k'){
    const arts=(adj[n.id]||[]).map(i=>byId[i]);
    el.innerHTML='<b class="kw">'+esc(n.label)+'</b> — '+arts.length+' article(s)<br>'+
      arts.slice(0,12).map(a=>'<span class="art">&#9679;</span> '+esc(a.label)).join('<br>')+
      (arts.length>12?'<br><span class="dim">…and '+(arts.length-12)+' more</span>':'');
  }else{
    el.innerHTML='<b class="art">'+esc(n.label)+'</b> <span class="dim">('+esc(n.src||'')+', '+esc(n.date||'')+')</span><br>'+
      esc(n.sum||'')+'<br><i>'+esc(n.take||'')+'</i><br>'+
      (adj[n.id]||[]).map(i=>'<span class="kw">'+esc(byId[i].label)+'</span>').join(' &middot; ')+
      (n.url?'<br><a href="'+n.url+'" target="_blank">open article</a>':'');
  }
}
tick();
</script>
</body>
</html>
"""


def main():
    articles = {a["id"]: a for a in common.load_articles()}
    ledger = [r for r in common.load_ledger().values() if r.get("status") == "done"]

    kw_count = {}
    for r in ledger:
        for k in r.get("keywords", []):
            kw_count[k] = kw_count.get(k, 0) + 1

    nodes = [{"id": "k:" + k, "label": k, "t": "k", "c": c} for k, c in kw_count.items()]
    links = []
    for r in ledger:
        a = articles.get(r["id"])
        if not a:
            continue
        nodes.append({"id": r["id"], "label": a["headline"][:90], "t": "a",
                      "src": a["source"], "date": a.get("date", ""), "url": a["url"],
                      "sum": r.get("summary", ""), "take": r.get("takeaway", "")})
        for k in r.get("keywords", []):
            links.append({"source": r["id"], "target": "k:" + k})

    data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.replace("__DATA__", data))
    print(f"wrote {OUT_PATH}: {len(nodes)} nodes, {len(links)} links")


if __name__ == "__main__":
    main()
