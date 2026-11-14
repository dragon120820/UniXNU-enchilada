"""Capture real compiler records and Mach-O objects, not a shim or symbol-name proxy."""
from pathlib import Path
import argparse,hashlib,json,shutil,struct
if not __debug__:raise RuntimeError('REFUSE optimized capture')
def exact_optin(arguments):
 definitions=[];i=0
 while i<len(arguments):
  arg=arguments[i];kind=None;value=None
  if arg in ('-D','-U'):
   kind=arg[1:];i+=1
   if i>=len(arguments):return False
   value=arguments[i]
  elif arg.startswith(('-D','-U')):kind=arg[1:2];value=arg[2:]
  if kind and value.split('=',1)[0]=='SWEET_MERKLE_ROOT':definitions.append((kind,value))
  i+=1
 return definitions==[('D','SWEET_MERKLE_ROOT=1')]
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists():raise RuntimeError('REFUSE output reuse')
a.out.mkdir(parents=True)
rows=[];errors=[]
for stem in ['sweet_ufs','verified_merkle','verified_merkle_io','verified_root_xnu_crypto']:
 candidates=list(a.root.rglob(stem+'.o.json'))
 if len(candidates)!=1:errors.append(f'{stem}: expected one compile record, got {len(candidates)}');continue
 record=candidates[0];blob=record.read_bytes();rec=json.loads(blob.decode().strip().rstrip(','));args=rec.get('arguments',[])
 if not isinstance(args,list) or not all(isinstance(x,str) for x in args):raise RuntimeError('Malformed compiler arguments')
 source=Path(rec['file']);source=source if source.is_absolute() else Path(rec['directory'])/source
 if source.name!=stem+'.c' or not source.is_file():raise RuntimeError('Wrong actual source')
 obj=record.with_suffix('');row=dict(name=stem,compiler_record=str(record),source=str(source),arguments=args,record_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
 shutil.copyfile(record,a.out/(stem+'.o.json'));shutil.copyfile(source,a.out/(stem+'.c'))
 if stem=='sweet_ufs' and not exact_optin(args):errors.append('Actual SWEET compiler record lacks a unique enabled optin macro')
 if not obj.is_file():errors.append(stem+': real object missing');rows.append(row);continue
 raw=obj.read_bytes()
 if len(raw)<32 or struct.unpack_from('<4I',raw)!=(0xfeedfacf,0x100000c,0,1):errors.append(stem+': not arm64 subtype0 Mach-O OBJECT')
 shutil.copyfile(obj,a.out/(stem+'.o'));row.update(object_sha256=hashlib.sha256(raw).hexdigest(),object_bytes=len(raw));rows.append(row)
result=dict(result='PASS' if not errors and len(rows)==4 else 'REJECT',objects=rows,errors=errors,scope='actual SDK compiler inputs/objects; not runtime, POST, root authority or hardware')
(a.out/'records.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if result['result']!='PASS':raise SystemExit(1)
