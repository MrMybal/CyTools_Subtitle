"""Native NVIDIA contracts and failure handling; no weights required for unit tests."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import pytest
from cytools_core import CyToolError, load_manifest
import nemotron
import speakers
import tool


def parameters(**updates):
    operation=next(o for o in load_manifest(tool.APP/'CyTool.json')['operations'] if o['id']=='diarize_subtitles')
    value={k:v['default'] for k,v in operation['inputSchema']['properties'].items() if 'default' in v}
    return {**value,'diarization_engine':'nemotron3',**updates}


def test_overlapping_native_turns_are_preserved_with_separate_exclusive_track():
    raw={'segments':[{'start':1.,'end':3.,'speaker':5},{'start':2.,'end':4.,'speaker':2}]};before=copy.deepcopy(raw)
    people,regular,exclusive=nemotron.normalize_segments(raw,10.)
    assert raw==before and [p['id'] for p in people]==['speaker-1','speaker-2']
    assert regular==[{'start':1.,'end':3.,'speaker':'speaker-1'},{'start':2.,'end':4.,'speaker':'speaker-2'}]
    assert exclusive==[{'start':1.,'end':3.,'speaker':'speaker-1'},{'start':3.,'end':4.,'speaker':'speaker-2'}]
    doc={'format':'cytools-subtitles','schemaVersion':1,'words':[],'cues':[{'id':'one','text':'A shared moment.','start':2.,'end':3.5,'kind':'speech'}]}
    result=speakers.attach(doc,{'model':nemotron.MODEL,'revision':'fixture','speakers':people,'segments':regular,'exclusiveSegments':exclusive})
    assert result['cues'][0]['speakerCandidates']==['speaker-2','speaker-1']


@pytest.mark.parametrize('turn',[{'start':float('nan'),'end':2.,'speaker':1},{'start':1.,'end':0.,'speaker':1},{'start':0.,'end':1.,'speaker':9},{'start':0.,'end':1.,'speaker':True}])
def test_native_invalid_timing_or_identity_is_rejected(turn):
    with pytest.raises(ValueError):nemotron.normalize_segments({'segments':[turn]},10.)


def test_native_options_refuse_foreign_knobs_and_inactive_custom_geometry():
    assert nemotron.options(parameters())['nemotron_mode']=='chunked'
    for updates in ({'speaker_count':2},{'embedding_batch_size':2},{'nemotron_chunk':200},{'nemotron_mode':'full','nemotron_preset':'custom'}):
        with pytest.raises(ValueError):nemotron.options(parameters(**updates))
    assert nemotron.options(parameters(nemotron_preset='custom',nemotron_chunk=200))['nemotron_chunk']==200
    assert nemotron.options(parameters(nemotron_min_duration_on=0))['nemotron_min_duration_on']==0


def test_runtime_marker_cannot_escape_private_root(tmp_path):
    base=tmp_path/'runtime/components/nemotron/cpu';base.mkdir(parents=True)
    nemotron.atomic(base/'active.json',{'schemaVersion':1,'directory':'../../../outside','archiveSha256':nemotron.CATALOG['runtimes']['cpu']['sha256'],'files':{'file':'hash'}})
    assert nemotron.active_runtime(tmp_path,'cpu') is None
    assert not nemotron.status(tmp_path)['ready']


def test_native_archive_traversal_is_refused(tmp_path):
    archive=tmp_path/'unsafe.zip'
    with zipfile.ZipFile(archive,'w') as z:z.writestr('../outside.txt','untrusted')
    with pytest.raises(ValueError,match='Unsafe'):nemotron.extract_verified(archive,tmp_path/'candidate')
    assert not (tmp_path/'outside.txt').exists()


def test_failed_candidate_does_not_replace_previous_activation(tmp_path,monkeypatch):
    archive=tmp_path/'candidate.zip';relative=nemotron.CATALOG['runtimes']['cpu']['executable']
    with zipfile.ZipFile(archive,'w') as z:z.writestr(relative,b'fixture')
    base=tmp_path/'runtime/components/nemotron/cpu';base.mkdir(parents=True);marker=base/'active.json';marker.write_text('{"directory":"previous"}')
    before=marker.read_bytes()
    monkeypatch.setattr(nemotron,'download',lambda root,reference,license_accepted:archive)
    def probe(exe,args,root,timeout=120):
        return subprocess.CompletedProcess(args,0,'nemo-speech 0.2.0\n' if args==['--version'] else '{"features":{"diarization":false}}','')
    monkeypatch.setattr(nemotron,'command',probe)
    with pytest.raises(RuntimeError,match='does not expose'):nemotron.install_runtime(tmp_path,'cpu',license_accepted=True)
    assert marker.read_bytes()==before


def test_explicit_license_and_authenticated_network_are_required(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,'ROOT',tmp_path)
    with tool.create_runtime(tmp_path/'jobs') as runtime:
        actor=runtime.authenticate(runtime.create_client('Ordinary')['token']);sid=runtime.create_session(actor)['sessionId']
        with pytest.raises(CyToolError):runtime.submit(actor,sid,'install_nemotron_model',{'license_accepted':True})
        owner=runtime.authenticate(runtime.create_client('Installer',permissions=['network'])['token']);session=runtime.create_session(owner)['sessionId']
        job=runtime.wait(owner,runtime.submit(owner,session,'install_nemotron_runtime',{'backend':'cpu'})['jobId'],timeout=10)
        assert job['state']=='Failed' and job['error']['code']=='LicenseAcceptanceRequired'
        assert not (tmp_path/'runtime/components/nemotron/cpu/active.json').exists()
    with pytest.raises(ValueError,match='Explicit'):nemotron.download(tmp_path,nemotron.CATALOG['model'],False)


def test_local_model_hashes_cannot_be_relabelled_as_compatible(tmp_path,monkeypatch):
    path=tmp_path/'model.gguf';path.write_bytes(b'GGUF fixture')
    catalog=copy.deepcopy(nemotron.CATALOG);catalog['model'].update(size=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    monkeypatch.setattr(nemotron,'CATALOG',catalog)
    assert nemotron.verify_model(path)['path']==str(path)
    path.write_bytes(b'GGUF changed')
    with pytest.raises(ValueError,match='checksum'):nemotron.verify_model(path)


def test_cross_model_manual_identities_require_explicit_replacement():
    from test_speakers import document,analysis
    original=speakers.attach(document(),analysis());original=speakers.rename(original,{'speaker-1':'Alice'})
    original['cues'][0]['speakerManual']=True
    replacement={**analysis(),'model':nemotron.MODEL}
    with pytest.raises(ValueError,match='explicit replacement'):speakers.attach(original,replacement)
    result=speakers.attach(original,replacement,replace_manual=True)
    assert result['speakers'][0]['name']=='Person 1' and not result['cues'][0]['speakerManual']
    assert original['speakers'][0]['name']=='Alice' and original['cues'][0]['speakerManual']


def test_cuda_reservation_is_distinct_from_cpu_and_full_mode_is_conservative(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,'ROOT',tmp_path)
    with tool.create_runtime(tmp_path/'jobs') as runtime:
        cpu=runtime.estimate_resources('diarize_subtitles',{'media':'voice.wav','document':'captions.json','diarization_engine':'nemotron3','nemotron_device':'cpu'})
        gpu=runtime.estimate_resources('diarize_subtitles',{'media':'voice.wav','document':'captions.json','diarization_engine':'nemotron3','nemotron_device':'cuda'})
        full=runtime.estimate_resources('diarize_subtitles',{'media':'voice.wav','document':'captions.json','diarization_engine':'nemotron3','nemotron_device':'cuda','nemotron_mode':'full'})
        assert not cpu.get('vramBytes') and gpu['vramBytes']['0']>=2*1024**3 and full['vramBytes']['0']>gpu['vramBytes']['0']


def test_cpu_cap_is_inherited_by_child_without_mutating_test_process():
    if sys.platform!='win32':pytest.skip('Windows native integration')
    script="import ctypes,json,nemotron,subprocess,sys;count=nemotron.limit_cpu(2);code=\"import ctypes; k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p;k.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)];a=ctypes.c_size_t();b=ctypes.c_size_t();k.GetProcessAffinityMask(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b));print(a.value.bit_count())\";p=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,check=True);print(json.dumps({'worker':count,'child':int(p.stdout)}))"
    result=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True,check=True,creationflags=0x08000000)
    assert json.loads(result.stdout)=={'worker':2,'child':2}


@pytest.mark.parametrize('files',['invalid',{'file.exe':None}])
def test_corrupted_runtime_file_index_reports_missing(tmp_path,files):
    reference=nemotron.CATALOG['runtimes']['cpu']
    base=tmp_path/'runtime/components/nemotron/cpu';candidate=base/'candidate'
    executable=candidate/reference['executable'];executable.parent.mkdir(parents=True);executable.write_bytes(b'fixture')
    nemotron.atomic(base/'active.json',{'schemaVersion':1,'directory':'candidate','archiveSha256':reference['sha256'],'files':files})
    assert nemotron.active_runtime(tmp_path,'cpu',verify=True) is None
