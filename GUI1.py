import tkinter as tk
from tkinter import filedialog, messagebox
import threading, shutil, time, os
from pathlib import Path

BG  = "#0D0F14"   # Background color
PAN = "#161B26"   # Panel color
ACC = "#00C9A7"   # Accent color (like highlights/buttons)
RED = "#FF6B6B"   # Error or warning color
TXT = "#E8EAF0"   # Text color
DIM = "#6B7280"   # Dim/secondary text color
MF=("Courier New",10); MB=("Courier New",10,"bold"); MT=("Courier New",18,"bold")

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("DriveShift"); self.geometry("860x680"); self.configure(bg=BG); self.resizable(1,1)
        self.src=tk.StringVar(); self.dst=tk.StringVar(); self.op=tk.StringVar(value="copy")
        self._cancel=False; self._pause=False; self.speeds=[]; self._build()

    def _build(self):
        tk.Label(self,text="⟳ DriveShift",font=MT,bg=BG,fg=ACC).pack(anchor="w",padx=20,pady=(14,0))
        tk.Frame(self,bg=DIM,height=1).pack(fill="x",padx=20,pady=8)
        f=tk.Frame(self,bg=BG); f.pack(fill="x",padx=20); f.columnconfigure(1,weight=1)
        for r,(lbl,var,cmd,col) in enumerate([("SOURCE",self.src,self._bsrc,ACC),("DESTINATION",self.dst,self._bdst,RED)]):
            tk.Label(f,text=lbl,font=MF,bg=BG,fg=DIM).grid(row=r*2,column=0,columnspan=3,sticky="w")
            tk.Entry(f,textvariable=var,bg=PAN,fg=TXT,insertbackground=TXT,font=MF,relief="flat",bd=0).grid(row=r*2+1,column=0,columnspan=2,sticky="ew",padx=(0,8),ipady=5,pady=(2,8))
            tk.Button(f,text="Browse",command=cmd,bg=PAN,fg=col,relief="flat",font=MF,cursor="hand2").grid(row=r*2+1,column=2,pady=(2,8))
        lb=tk.Frame(self,bg=BG); lb.pack(fill="x",padx=20)
        tk.Label(lb,text="FILES TO TRANSFER",font=MF,bg=BG,fg=DIM).pack(anchor="w")
        lw=tk.Frame(lb,bg=PAN); lw.pack(fill="x",pady=4)
        sb=tk.Scrollbar(lw); sb.pack(side="right",fill="y")
        self.lb=tk.Listbox(lw,bg=PAN,fg=TXT,selectbackground=ACC,selectforeground=BG,font=MF,height=5,bd=0,highlightthickness=0,yscrollcommand=sb.set,activestyle="none"); self.lb.pack(fill="x",padx=6,pady=4); sb.config(command=self.lb.yview)
        br=tk.Frame(lb,bg=BG); br.pack(fill="x",pady=4)
        for t,c in [("＋ Files",self._af),("＋ Folder",self._afd),("✕ Remove",self._rm),("✕ Clear",self._cl)]:
            tk.Button(br,text=t,command=c,bg=PAN,fg=ACC if "＋" in t else RED,relief="flat",font=MF,cursor="hand2",padx=8,pady=3).pack(side="left",padx=(0,6))
        op=tk.Frame(self,bg=BG); op.pack(fill="x",padx=20,pady=4)
        tk.Label(op,text="OPERATION:",font=MF,bg=BG,fg=DIM).pack(side="left")
        for v,l in [("copy","Copy"),("move","Move & Delete"),("sync","Sync")]:
            tk.Radiobutton(op,text=l,variable=self.op,value=v,bg=BG,fg=TXT,selectcolor=BG,activebackground=BG,activeforeground=ACC,font=MF).pack(side="left",padx=10)
        pr=tk.Frame(self,bg=BG); pr.pack(fill="x",padx=20,pady=(6,0))
        self.slbl=tk.Label(pr,text="Ready",font=MF,bg=BG,fg=DIM,anchor="w");
        self.slbl.pack(side="left")
        self.plbl=tk.Label(pr,text="0%",font=MB,bg=BG,fg=ACC,anchor="e");
        self.plbl.pack(side="right")
        pb=tk.Frame(self,bg=DIM,height=8); pb.pack(fill="x",padx=20,pady=4)
        self.pbar=tk.Frame(pb,bg=ACC,height=8);
        self.pbar.place(x=0,y=0,relheight=1,relwidth=0)
        si=tk.Frame(self,bg=BG); si.pack(fill="x",padx=20)
        self.spd=tk.Label(si,text="Speed: —",font=MF,bg=BG,fg=DIM);
        self.spd.pack(side="left")
        self.eta=tk.Label(si,text="ETA: —",font=MF,bg=BG,fg=DIM);
        self.eta.pack(side="left",padx=12)
        self.flbl=tk.Label(si,text="",font=MF,bg=BG,fg=DIM);
        self.flbl.pack(side="right")
        tk.Label(self,text="LIVE SPEED (MB/s)",font=MF,bg=BG,fg=DIM).pack(anchor="w",padx=20,pady=(8,0))
        self.cv=tk.Canvas(self,bg=PAN,height=150,highlightthickness=0);
        self.cv.pack(fill="both",expand=True,padx=20,pady=(4,0))
        self.cv.bind("<Configure>",lambda e:self._draw())
        ar=tk.Frame(self,bg=BG); ar.pack(fill="x",padx=20,pady=12)
        self.sb2=tk.Button(ar,text="▶ START",command=self._start,bg=PAN,fg=ACC,relief="flat",font=MB,cursor="hand2",padx=18,pady=8); self.sb2.pack(side="left",padx=(0,8))
        self.pb2=tk.Button(ar,text="⏸ PAUSE",command=self._pause_tog,bg=PAN,fg=TXT,relief="flat",font=MF,cursor="hand2",padx=12,pady=8,state="disabled"); self.pb2.pack(side="left",padx=(0,8))
        self.cb=tk.Button(ar,text="■ CANCEL",command=self._do_cancel,bg=PAN,fg=RED,relief="flat",font=MF,cursor="hand2",padx=12,pady=8,state="disabled"); self.cb.pack(side="left")
        self.tot=tk.Label(ar,text="",font=MF,bg=BG,fg=DIM); self.tot.pack(side="right")

    def _bsrc(self): d=filedialog.askdirectory(); self.src.set(d) if d else None
    def _bdst(self): d=filedialog.askdirectory(); self.dst.set(d) if d else None
    def _af(self):
        for f in filedialog.askopenfilenames(initialdir=self.src.get() or "/"):
            if f not in self.lb.get(0,"end"): self.lb.insert("end",f)
    def _afd(self):
        d=filedialog.askdirectory(initialdir=self.src.get() or "/")
        if d: [self.lb.insert("end",str(f)) for f in Path(d).rglob("*") if f.is_file() and str(f) not in self.lb.get(0,"end")]
    def _rm(self): [self.lb.delete(i) for i in reversed(self.lb.curselection())]
    def _cl(self): self.lb.delete(0,"end")
    def _pause_tog(self): self._pause=not self._pause; self.pb2.config(text="▶ RESUME" if self._pause else "⏸ PAUSE")
    def _do_cancel(self): self._cancel=True; self._pause=False

    def _draw(self):
        self.cv.delete("all"); W=self.cv.winfo_width(); H=self.cv.winfo_height()
        if W<10 or len(self.speeds)<2: return
        pl,pr,pt,pb=44,10,10,24; gw=W-pl-pr; gh=H-pt-pb
        mx=max(max(self.speeds),.1)
        for i in range(5):
            y=pt+gh-(i/4)*gh; self.cv.create_line(pl,y,W-pr,y,fill=DIM,dash=(3,4))
            self.cv.create_text(pl-4,y,text=f"{(i/4)*mx:.1f}",anchor="e",fill=DIM,font=("Courier New",8))
        n=len(self.speeds); pts=[pl,pt+gh]
        for i,v in enumerate(self.speeds): pts+=[pl+(i/(max(n-1,1)))*gw, pt+gh-(v/mx)*gh]
        pts+=[pl+((n-1)/(max(n-1,1)))*gw,pt+gh]
        self.cv.create_polygon(pts,fill="#00C9A720",outline="")
        lp=[]
        for i,v in enumerate(self.speeds): lp+=[pl+(i/(max(n-1,1)))*gw, pt+gh-(v/mx)*gh]
        self.cv.create_line(lp,fill=ACC,width=2,smooth=True)
        lx,ly=pl+((n-1)/(max(n-1,1)))*gw,pt+gh-(self.speeds[-1]/mx)*gh
        self.cv.create_oval(lx-4,ly-4,lx+4,ly+4,fill=ACC,outline=BG,width=2)
        self.cv.create_text(W//2,H-6,text="time →",fill=DIM,font=("Courier New",8))

    def _start(self):
        dst=self.dst.get().strip()
        if not dst or not os.path.isdir(dst): return messagebox.showerror("Error","Set a valid destination folder.")
        files=[Path(self.lb.get(i)) for i in range(self.lb.size())]
        if not files: return messagebox.showerror("Error","Add files first.")
        self._cancel=False; self._pause=False; self.speeds=[]
        self.sb2.config(state="disabled"); self.pb2.config(state="normal"); self.cb.config(state="normal")
        threading.Thread(target=self._worker,args=(files,Path(dst)),daemon=True).start()

    def _worker(self,files,dst):
        total=sum(f.stat().st_size for f in files if f.is_file()); done=0; op=self.op.get(); win=[]
        for idx,f in enumerate(files):
            if self._cancel: break
            if not f.is_file(): continue
            self.after(0,self.slbl.config,{"text":f"[{idx+1}/{len(files)}] {f.name}"}); self.after(0,self.flbl.config,{"text":f"▸ {f.name}"})
            df=dst/f.name; df.parent.mkdir(parents=True,exist_ok=True)
            try:
                with open(f,"rb") as fi, open(df,"wb") as fo:
                    while not self._cancel:
                        while self._pause: time.sleep(.2)
                        buf = fi.read(524288)
                        time.sleep(0.02)  # 👈 ADD THIS LINE (simulate real transfer time)
                        if not buf: break
                        fo.write(buf); done+=len(buf); now=time.perf_counter()
                        win.append((now,len(buf))); win=[x for x in win if now-x[0]<=1]
                        spd=sum(b for _,b in win)/(now-win[0][0]+.001)/1e6 if len(win)>1 else 0
                        self.speeds.append(spd);
                        if len(self.speeds)>60: self.speeds.pop(0)
                        pct=done/total if total else 0; eta=(total-done)/(spd*1e6+1)
                        self.after(0,self._upd,pct,spd,eta,done,total)
            except Exception as e: self.after(0,messagebox.showerror,"Error",str(e)); break
            if op in("move","sync") and not self._cancel and df.exists():f.unlink(missing_ok=True)
        msg="✓ Done!" if not self._cancel else "Cancelled."
        self.after(0,self.slbl.config,{"text":msg,"fg":ACC if not self._cancel else RED})
        if not self._cancel: self.after(0,self._upd,1,0,0,total,total)
        self.after(0,self.sb2.config,{"state":"normal"}); self.after(0,self.pb2.config,{"state":"disabled","text":"⏸ PAUSE"}); self.after(0,self.cb.config,{"state":"disabled"}); self.after(0,self.flbl.config,{"text":""})

    def _upd(self,pct,spd,eta,done,total):
        self.pbar.place(relwidth=pct); self.plbl.config(text=f"{int(pct*100)}%")
        self.spd.config(text=f"Speed: {max(spd, 0.01):.2f} MB/s")
        m,s=divmod(int(eta),60); self.eta.config(text=f"ETA: {m}m {s:02d}s" if eta>0 else "ETA: —")
        self.tot.config(text=f"{done/1e6:.1f} / {total/1e6:.1f} MB")
        self._draw()

if __name__=="__main__": App().mainloop()