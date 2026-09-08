from flask import Flask, request, send_from_directory, render_template_string
from pathlib import Path
import subprocess, zipfile, shutil, os

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'input'
WORK = ROOT / 'work'
OUTPUT = ROOT / 'output'
for p in (INPUT, WORK, OUTPUT): p.mkdir(exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

HTML = '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>PS1 BIN Builder</title><style>body{font-family:-apple-system,system-ui;background:#111;color:#eee;padding:18px;max-width:700px;margin:auto}h1{font-size:26px}section{background:#1d1d1f;padding:16px;border-radius:16px;margin:14px 0}input,button{font-size:16px;margin:8px 0;width:100%}button{padding:12px;border:0;border-radius:12px}pre{white-space:pre-wrap;background:#000;padding:12px;border-radius:12px;overflow:auto}a{color:#7ab7ff}</style></head><body><h1>PS1 BIN Builder</h1><p>واجهة مبسطة للآيفون.</p><section><h2>1) استخراج القرص الأصلي</h2><form method="post" action="/dump" enctype="multipart/form-data"><label>اختر ملف CUE</label><input type="file" name="cue" required><label>اختر ملف BIN</label><input type="file" name="bin" required><button type="submit">رفع واستخراج</button></form></section><section><h2>2) بناء BIN/CUE من ZIP</h2><p>ارفع ZIP يحتوي على layout.xml ومجلد files.</p><form method="post" action="/build" enctype="multipart/form-data"><input type="file" name="zip" accept=".zip" required><button type="submit">بناء اللعبة</button></form></section><section><h2>النتائج</h2>{downloads}</section>{log}</body></html>'''

def page(msg=''):
    links=[]
    for f in sorted(OUTPUT.glob('*')):
        if f.is_file(): links.append(f'<p><a href="/download/{f.name}">{f.name}</a> ({f.stat().st_size/1024/1024:.1f} MB)</p>')
    log = f'<section><h2>النتيجة</h2><pre>{msg}</pre></section>' if msg else ''
    return render_template_string(HTML, downloads=''.join(links) or '<p>لا توجد ملفات بعد.</p>', log=log)

@app.get('/')
def home(): return page()

@app.post('/dump')
def dump():
    try:
        shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
        cue=request.files['cue']; binf=request.files['bin']
        cue_path=INPUT/cue.filename; bin_path=INPUT/binf.filename
        cue.save(cue_path); binf.save(bin_path)
        # Ensure CUE points to uploaded BIN filename.
        txt=cue_path.read_text(errors='ignore')
        import re
        txt=re.sub(r'FILE\s+"[^"]+"\s+BINARY', f'FILE "{bin_path.name}" BINARY', txt, flags=re.I)
        cue_path.write_text(txt)
        cmd=[str(ROOT/'dumpsxiso'), str(cue_path), '-x', str(WORK/'files'), '-s', str(WORK/'layout.xml')]
        r=subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode: return page('فشل الاستخراج:\n'+r.stdout)
        zip_path=OUTPUT/'extracted_ps1.zip'
        if zip_path.exists(): zip_path.unlink()
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', WORK)
        return page('تم الاستخراج بنجاح. نزّل extracted_ps1.zip وعدّل الملفات داخله ثم ارفعه في الخطوة 2.\n\n'+r.stdout)
    except Exception as e: return page('خطأ: '+repr(e))

@app.post('/build')
def build():
    try:
        shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
        f=request.files['zip']; zp=INPUT/'build_input.zip'; f.save(zp)
        with zipfile.ZipFile(zp) as z:
            z.extractall(WORK)
        xmls=list(WORK.rglob('layout.xml'))
        if not xmls: return page('لم أجد layout.xml داخل ZIP.')
        xml=xmls[0]
        # dumpsxiso archives may have files next to layout.xml; keep paths intact.
        outbin=OUTPUT/'game.bin'; outcue=OUTPUT/'game.cue'
        for x in (outbin,outcue):
            if x.exists(): x.unlink()
        cmd=[str(ROOT/'mkpsxiso'), str(xml), '-o', str(outbin), '-c', str(outcue)]
        r=subprocess.run(cmd, cwd=xml.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode: return page('فشل البناء:\n'+r.stdout)
        return page('تم بناء BIN/CUE بنجاح.\n\n'+r.stdout)
    except Exception as e: return page('خطأ: '+repr(e))

@app.get('/download/<name>')
def download(name): return send_from_directory(OUTPUT, name, as_attachment=True)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)
