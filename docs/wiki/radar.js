/* AERead interactive multi-model exploitability radar. Toggle models to overlay.
   Raw exploitability per axis (lower=better), identical to the leaderboard.
   6 axes = the discriminating cases. Static file (no markdown processing). */
(function(){
  "use strict";
  var DATA={"claude-opus-4.8": {"vals": {"rps": 0.3262, "kuhn_poker": 0.2778, "wrps": 0.318, "intertemporal": 0.0243, "cross_modality": 0.0, "allais": 0.0}, "light": 0, "mean": 0.158}, "claude-sonnet-4.6": {"vals": {"rps": 0.2128, "kuhn_poker": 0.1111, "wrps": 0.2465, "intertemporal": 0.0477, "cross_modality": 0.0, "allais": 0.0}, "light": 0, "mean": 0.103}, "claude-opus-4.5": {"vals": {"rps": 0.3475, "kuhn_poker": 0.1111, "wrps": 0.342, "intertemporal": 0.6447, "cross_modality": 0.0, "allais": 0.0}, "light": 0, "mean": 0.241}, "gpt-5.1": {"vals": {"rps": 0.6073, "kuhn_poker": 0.4444, "wrps": 0.4487, "intertemporal": 0.0263, "cross_modality": 0.0, "allais": 0.625}, "light": 0, "mean": 0.359}, "gemini-2.5-flash": {"vals": {"rps": 0.6839, "kuhn_poker": 0.1111, "wrps": 0.5638, "intertemporal": 0.7204, "cross_modality": 0.75, "allais": 0.0}, "light": 0, "mean": 0.472}, "grok-4.3": {"vals": {"rps": 0.3745, "kuhn_poker": 0.1111, "wrps": 0.2216, "intertemporal": 0.0, "cross_modality": 0.0, "allais": 0.0}, "light": 0, "mean": 0.118}, "gpt-5.5": {"vals": {"rps": 0.2258, "kuhn_poker": 0.2778, "wrps": 0.2258, "intertemporal": 0.0, "cross_modality": 0.0, "allais": 0.0}, "light": 1, "mean": 0.122}, "gemini-3.5-flash": {"vals": {"rps": 0.7419, "kuhn_poker": 0.2778, "wrps": 0.5726, "intertemporal": 0.2642, "cross_modality": 0.0, "allais": 0.0}, "light": 1, "mean": 0.309}}, ORDER=["claude-sonnet-4.6", "grok-4.3", "gpt-5.5", "claude-opus-4.8", "claude-opus-4.5", "gemini-3.5-flash", "gpt-5.1", "gemini-2.5-flash"], COLORS={"claude-sonnet-4.6": "#4daf4a", "grok-4.3": "#a65628", "gpt-5.5": "#377eb8", "claude-opus-4.8": "#984ea3", "claude-opus-4.5": "#f781bf", "gemini-3.5-flash": "#ff7f00", "gpt-5.1": "#999999", "gemini-2.5-flash": "#e41a1c"}, DEFAULT=["claude-opus-4.8", "gpt-5.5", "gemini-3.5-flash"];
  var AXES=[["Randomization","rps"],["Strategic","kuhn"],["Eq-computation","wrps"],
            ["Time","intertemporal"],["Framing","cross-modality"],["Time-risk","allais"]];
  var KEYS=["rps","kuhn_poker","wrps","intertemporal","cross_modality","allais"];
  var VMAX=0.75, cx=245, cy=215, R=145, N=6;
  function mid(m){return m.replace(/[^a-z0-9]/gi,"_");}
  function P(i,v){var a=(-90+60*i)*Math.PI/180,r=R*Math.min(v,VMAX)/VMAX;return [cx+r*Math.cos(a),cy+r*Math.sin(a)];}
  function ring(f){var p=[];for(var i=0;i<N;i++){var a=(-90+60*i)*Math.PI/180,r=R*f;p.push((cx+r*Math.cos(a)).toFixed(1)+","+(cy+r*Math.sin(a)).toFixed(1));}return p.join(" ");}
  function poly(m){var p=[];for(var i=0;i<N;i++){var xy=P(i,DATA[m].vals[KEYS[i]]);p.push(xy[0].toFixed(1)+","+xy[1].toFixed(1));}return p.join(" ");}
  function checked(){return ORDER.filter(function(m){var e=document.getElementById("aer-cb-"+mid(m));return e&&e.checked;});}
  function svg(models){
    var s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 470" width="490" style="max-width:100%;height:auto" font-family="sans-serif" role="img" aria-label="multi-model exploitability radar">';
    s+='<rect x="0" y="0" width="490" height="470" fill="#ffffff"/>';
    [0.3333,0.6667,1.0].forEach(function(f){s+='<polygon points="'+ring(f)+'" fill="none" stroke="#dddddd" stroke-width="1"/>';});
    [[0.25,0.3333],[0.50,0.6667],[0.75,1.0]].forEach(function(rv){s+='<text x="'+(cx+3)+'" y="'+(cy-R*rv[1]+3).toFixed(1)+'" font-size="8.5" fill="#bbbbbb">'+rv[0].toFixed(2)+'</text>';});
    for(var i=0;i<N;i++){
      var tip=P(i,VMAX),a=(-90+60*i)*Math.PI/180;
      s+='<line x1="'+cx+'" y1="'+cy+'" x2="'+tip[0].toFixed(1)+'" y2="'+tip[1].toFixed(1)+'" stroke="#ececec" stroke-width="1"/>';
      var lx=cx+(R+20)*Math.cos(a),ly=cy+(R+20)*Math.sin(a);
      var anc=Math.abs(Math.cos(a))<0.3?"middle":(Math.cos(a)>0?"start":"end");
      var dy=Math.sin(a)<-0.3?-3:(Math.sin(a)>0.3?11:4);
      s+='<text x="'+lx.toFixed(1)+'" y="'+(ly+dy).toFixed(1)+'" font-size="11" font-weight="700" fill="#333" text-anchor="'+anc+'">'+AXES[i][0]+'</text>';
      s+='<text x="'+lx.toFixed(1)+'" y="'+(ly+dy+11).toFixed(1)+'" font-size="8.5" fill="#999" text-anchor="'+anc+'">'+AXES[i][1]+'</text>';
    }
    models.forEach(function(m){
      s+='<polygon points="'+poly(m)+'" fill="'+COLORS[m]+'" fill-opacity="0.10" stroke="'+COLORS[m]+'" stroke-width="2.3"/>';
      for(var i=0;i<N;i++){var xy=P(i,DATA[m].vals[KEYS[i]]);s+='<circle cx="'+xy[0].toFixed(1)+'" cy="'+xy[1].toFixed(1)+'" r="2.6" fill="'+COLORS[m]+'"/>';}
    });
    if(models.length===1){
      var m=models[0];
      for(var i=0;i<N;i++){var v=DATA[m].vals[KEYS[i]],xy=P(i,v),a=(-90+60*i)*Math.PI/180;
        s+='<text x="'+(xy[0]+10*Math.cos(a)).toFixed(1)+'" y="'+(xy[1]+10*Math.sin(a)+3).toFixed(1)+'" font-size="9.5" font-weight="700" fill="'+COLORS[m]+'" text-anchor="middle">'+v.toFixed(3)+'</text>';}
    }
    s+='</svg>';return s;
  }
  function readout(models){
    if(!models.length) return '<p style="color:#888">Select one or more models above.</p>';
    var h='<table style="border-collapse:collapse;font-size:.84em;margin:0 auto"><tr><th style="text-align:left;padding:2px 8px">model</th><th style="padding:2px 6px">6-axis mean &#8595;</th>';
    AXES.forEach(function(a){h+='<th style="padding:2px 6px">'+a[1]+'</th>';});
    h+='</tr>';
    models.forEach(function(m){
      h+='<tr><td style="padding:2px 8px;white-space:nowrap"><span style="display:inline-block;width:10px;height:10px;background:'+COLORS[m]+';margin-right:5px"></span>'+m+(DATA[m].light?' <sup>&dagger;</sup>':'')+'</td>';
      h+='<td style="text-align:center;padding:2px 6px"><strong>'+DATA[m].mean.toFixed(3)+'</strong></td>';
      KEYS.forEach(function(k){h+='<td style="text-align:center;padding:2px 6px">'+DATA[m].vals[k].toFixed(3)+'</td>';});
      h+='</tr>';
    });
    h+='</table><p style="font-size:.78em;color:#999;margin:.4em 0">raw exploitability, lower = better &#183; radius scaled to 0.75 &#183; <sup>&dagger;</sup> lighter sampling (N=32,K=1,4 seeds)</p>';
    return h;
  }
  function render(){var ms=checked();document.getElementById("aer-svg").innerHTML=svg(ms);document.getElementById("aer-readout").innerHTML=readout(ms);}
  var box=document.getElementById("aer-controls");
  if(!box) return;
  ORDER.forEach(function(m){
    var lab=document.createElement("label");
    lab.style.cssText="display:inline-flex;align-items:center;margin:2px 8px;font-size:.85em;white-space:nowrap;cursor:pointer";
    var cb=document.createElement("input");cb.type="checkbox";cb.id="aer-cb-"+mid(m);cb.checked=DEFAULT.indexOf(m)>=0;cb.style.marginRight="4px";
    cb.addEventListener("change",render);
    var sw=document.createElement("span");sw.style.cssText="display:inline-block;width:11px;height:11px;background:"+COLORS[m]+";margin-right:4px;border-radius:2px";
    lab.appendChild(cb);lab.appendChild(sw);lab.appendChild(document.createTextNode(m));
    box.appendChild(lab);
  });
  render();
})();
