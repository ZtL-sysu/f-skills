import hashlib,json,subprocess,sys,uuid,tempfile
from pathlib import Path

temporary=tempfile.TemporaryDirectory(prefix='research-github-sync-test-')
base=Path(temporary.name).resolve()
root=(base/('fixture-'+uuid.uuid4().hex[:8])).resolve()
assert root.is_relative_to(base.resolve())
root.mkdir()
script=Path(__file__).resolve().parents[1]/'scripts/checkpoint_manifest.py'
def cmd(*args,ok=True):
    p=subprocess.run(args,cwd=root,text=True,encoding='utf-8',capture_output=True)
    assert (p.returncode==0)==ok,(p.returncode,p.stdout,p.stderr)
    return p
def helper(*args,ok=True):return cmd(sys.executable,'-X','utf8',str(script),*args,ok=ok)
cmd('git','init','-q')
cmd('git','config','user.name','Fixture')
cmd('git','config','user.email','fixture@example.invalid')
(root/'protocol.md').write_text('Frozen synthetic fixture protocol\n')
(root/'result.json').write_text('{"fixture_only":true,"value":42}\n')
(root/'unrelated.txt').write_text('do not stage this\n')
cmd('git','add','protocol.md')
cmd('git','commit','-qm','fixture protocol')
before=cmd('git','diff','--cached','--name-only').stdout
out='collaboration/tasks/e0/agents/test-agent/checkpoints/20261113T000000Z-test/manifest.json'
args=['create','--repo',str(root),'--task','e0','--agent','test-agent','--status','in_progress',
      '--protocol','protocol.md','--artifact','result.json','--out',out]
helper(*args)
helper('verify','--repo',str(root),'--manifest',out)
doc=json.loads((root/out).read_text())
assert doc['artifacts'][0]['sha256']==hashlib.sha256((root/'result.json').read_bytes()).hexdigest()
assert doc['artifacts'][0]['path']=='result.json'
helper(*args,ok=False) # immutable checkpoint
(root/'result.json').write_text('{"fixture_only":true,"value":43}\n')
helper('verify','--repo',str(root),'--manifest',out,ok=False) # real tampering detected
bad=list(args);bad[bad.index(out)]=out.replace('000000','000001');bad[bad.index('result.json')]='../outside.txt'
helper(*bad,ok=False)
(root/'credentials.json').write_text('{"fixture_only":true}\n')
bad=list(args);bad[bad.index(out)]=out.replace('000000','000002');bad[bad.index('result.json')]='credentials.json'
helper(*bad,ok=False)
with (root/'oversize.bin').open('wb') as f:f.truncate(50*1024*1024+1)
bad=list(args);bad[bad.index(out)]=out.replace('000000','000003');bad[bad.index('result.json')]='oversize.bin'
helper(*bad,ok=False)
assert cmd('git','diff','--cached','--name-only').stdout==before # helper never stages
assert cmd('git','log','--oneline').stdout.count('\n')==1 # helper never commits
print(json.dumps({'status':'pass','checks':['create+hash verification','tamper rejection','immutable checkpoint','path escape rejection','credential-like path rejection','oversize rejection','no staging or commits'],'fixture':'local synthetic; not research evidence'}))

assert root.is_relative_to(base)
temporary.cleanup()
