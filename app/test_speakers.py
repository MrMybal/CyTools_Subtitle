import copy
import json
from pathlib import Path
import pytest
from cytools_core import CyToolError
import diarization
import speakers
import subtitles
import tool


def document():
    return {'format':'cytools-subtitles','schemaVersion':1,'words':[{'text':'Hello','start':0.,'end':.6},{'text':'there.','start':.7,'end':1.2},{'text':'Goodbye.','start':1.3,'end':2.}], 'cues':[{'id':'one','start':0.,'end':2.,'text':'Manually edited line.','kind':'speech'},{'id':'sound','start':2.2,'end':3.,'text':'[door]','kind':'sound'}]}


def analysis():
    turns=[{'start':0.,'end':1.25,'speaker':'speaker-1'},{'start':1.25,'end':2.1,'speaker':'speaker-2'}]
    return {'model':diarization.MODEL,'revision':'fixture','mediaSha256':'same-recording','device':'cpu','speakers':[{'id':'speaker-1','name':'Person 1'},{'id':'speaker-2','name':'Person 2'}],'segments':copy.deepcopy(turns),'exclusiveSegments':turns}


def test_attribution_preserves_manual_text_times_and_raw_words(tmp_path):
    original=document();before=copy.deepcopy(original);result=speakers.attach(original,analysis())
    assert original==before and result['words']==before['words']
    assert [(c['text'],c['start'],c['end']) for c in result['cues']]==[(c['text'],c['start'],c['end']) for c in before['cues']]
    assert result['cues'][0]['speaker']=='speaker-1' and len(result['cues'][0]['speakerCandidates'])==2
    assert result['cues'][1]==before['cues'][1]
    renamed=speakers.rename(result,{'speaker-1':'Alice','speaker-2':'Bob'})
    out=subtitles.save(renamed,tmp_path)
    assert '[Alice] Manually edited line.' in Path(out['srt']).read_text('utf-8')
    assert '[Alice] [door]' not in Path(out['srt']).read_text('utf-8')
    assert renamed['cues'][0]['text']=='Manually edited line.'
    hidden=speakers.rename(renamed,{},False)
    assert speakers.display_text(hidden,hidden['cues'][0])=='Manually edited line.'


def test_rebuild_splits_at_voice_change_and_manual_assignments_survive_analysis():
    source=document();rebuilt=speakers.attach(source,analysis(),rebuild=True)
    speech=[c for c in rebuilt['cues'] if c['kind']=='speech']
    assert len(speech)==2 and [c['speaker'] for c in speech]==['speaker-1','speaker-2']
    assert rebuilt['words']==source['words']
    manual=subtitles.edit(rebuilt,[{'id':speech[0]['id'],'speaker':'speaker-2'}])
    repeated=speakers.attach(manual,analysis())
    assert repeated['cues'][0]['speaker']=='speaker-2' and repeated['cues'][0]['speakerManual']
    forced=speakers.attach(manual,analysis(),replace_manual=True)
    assert forced['cues'][0]['speaker']=='speaker-1'


def test_timing_repair_does_not_merge_different_people():
    from timing import repair
    doc=speakers.attach(document(),analysis(),rebuild=True)
    result=repair(doc,max_cps=40,min_duration=.2)
    assert len([c for c in result['cues'] if c['kind']=='speech'])==2
    assert result['words']==doc['words']
    assert not any('_speakerPrefix' in c for c in result['cues'])


@pytest.mark.parametrize('change',[lambda d:d['speakers'].append(dict(d['speakers'][0])),lambda d:d['speakers'][0].update(name='bad\nname'),lambda d:d['cues'][0].update(speaker='missing'),lambda d:d['diarization']['exclusiveSegments'][1].update(start=.5),lambda d:d['diarization']['segments'][0].update(start=float('nan'))])
def test_invalid_speaker_metadata_rejected(change):
    doc=speakers.attach(document(),analysis());change(doc)
    with pytest.raises(ValueError):subtitles.validate(doc)


def test_uncovered_speech_stays_unassigned():
    result=speakers.attach(document(),{**analysis(),'segments':[],'exclusiveSegments':[]})
    assert result['cues'][0]['speaker'] is None and result['cues'][0]['speakerOverlapFraction']==0


def test_speaker_names_count_towards_reading_speed():
    doc=speakers.attach(document(),analysis());doc['cues'][0].update(text='Hi',end=.5)
    doc['speakers'][0]['name']='A very long name'
    assert subtitles.quality(doc)
    doc['speakerLabels']=False
    assert not subtitles.quality(doc)


def test_runtime_marker_confined_and_stale_lock_rejected(tmp_path):
    base=tmp_path/'runtime/components/diarization';base.mkdir(parents=True)
    (base/'active.json').write_text(json.dumps({'schemaVersion':1,'directory':'../../../../escape','lockSha256':'wrong'}))
    assert diarization.active_runtime(tmp_path) is None


def test_rename_roundtrip_through_runtime_and_private_task_cleanup(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,'ROOT',tmp_path)
    original=tmp_path/'outside captions é.json';original.write_text(json.dumps(speakers.attach(document(),analysis())),'utf-8')
    with tool.create_runtime(tmp_path/'jobs') as runtime:
        actor=runtime.authenticate(runtime.create_client('Speakers')['token']);session=runtime.create_session(actor)['sessionId']
        job=runtime.wait(actor,runtime.submit(actor,session,'rename_speakers',{'document':str(original),'names':{'speaker-1':'Alice'}})['jobId'],timeout=10)
        assert job['state']=='Completed',job
        path=Path(job['outputs']['document']);renamed=json.loads(path.read_text('utf-8'))
        assert renamed['speakers'][0]['name']=='Alice' and renamed['words']==document()['words']
        read=runtime.wait(actor,runtime.submit(actor,session,'read_subtitles',{'document':str(path)})['jobId'],timeout=10)
        assert read['state']=='Completed',read.get('error')
        assert read['outputs']['speakers'][0]['name']=='Alice'
        edited=runtime.wait(actor,runtime.submit(actor,session,'edit_subtitles',{'document':str(path),'edits':[{'id':'one','speaker':'speaker-2'}]})['jobId'],timeout=10)
        assert edited['state']=='Completed'
        exported=runtime.export_job(actor,edited['jobId'],str(tmp_path/'saved'))
        runtime.finish_task(actor,session)
        assert original.exists() and not path.exists() and Path(exported['outputs']['srt']).exists()


def test_installer_permissions_and_missing_model_are_explicit(tmp_path,monkeypatch):
    monkeypatch.setattr(tool,'ROOT',tmp_path)
    with tool.create_runtime(tmp_path/'jobs') as runtime:
        actor=runtime.authenticate(runtime.create_client('Ordinary')['token']);session=runtime.create_session(actor)['sessionId']
        with pytest.raises(CyToolError):runtime.submit(actor,session,'install_diarization_model',{'license_accepted':True})
        installer=runtime.authenticate(runtime.create_client('Installer',permissions=['network'])['token']);sid=runtime.create_session(installer)['sessionId']
        job=runtime.wait(installer,runtime.submit(installer,sid,'install_diarization_model',{})['jobId'],timeout=10)
        assert job['error']['code']=='LicenseAcceptanceRequired'
        job=runtime.wait(actor,runtime.submit(actor,session,'diarization_status',{})['jobId'],timeout=10)
        assert job['state']=='Completed' and not job['outputs']['runtimeReady']
        with pytest.raises(CyToolError):runtime.submit(actor,session,'diarize_subtitles',{'media':'x','document':'x','speaker_count':99})


def test_local_model_rejects_remote_asset_paths(tmp_path):
    (tmp_path/'config.yaml').write_text('pipeline:\n  name: pyannote.audio.pipelines.SpeakerDiarization\n  params:\n    embedding: other-org/model\n')
    with pytest.raises(ValueError,match='contained'):diarization.verify_model(tmp_path)


def test_failed_optional_install_keeps_previous_pointer(tmp_path,monkeypatch):
    import shutil,subprocess
    root=tmp_path;app=root/'app';(app/'packages').mkdir(parents=True)
    shutil.copyfile(tool.APP/'packages/pip-23.2.1-py3-none-any.whl',app/'packages/pip-23.2.1-py3-none-any.whl')
    (app/'requirements-diarization-windows.txt').write_text('# fixture')
    (app/'diarization-runtime-lock.json').write_text('{}')
    base=root/'runtime/components/diarization';base.mkdir(parents=True)
    marker=base/'active.json';marker.write_text('{"schemaVersion":1,"directory":"previous"}')
    before=marker.read_bytes();calls=[]
    def install_then_fail_probe(args,**kwargs):
        calls.append(args)
        if len(calls)==2:raise subprocess.CalledProcessError(1,args)
        return subprocess.CompletedProcess(args,0)
    monkeypatch.setattr(diarization.subprocess,'run',install_then_fail_probe)
    with pytest.raises(subprocess.CalledProcessError):diarization.install_runtime(root,base/'candidate')
    assert marker.read_bytes()==before


def test_model_hashes_checked_for_a_local_reference(tmp_path):
    path=tmp_path/'model';path.mkdir()
    (path/'config.yaml').write_text('pipeline:\n  name: pyannote.audio.pipelines.SpeakerDiarization\n  params:\n    embedding: $model/embedding\n    segmentation: $model/segmentation\n    plda: $model/plda\n')
    for name in diarization.FILES:
        if name=='config.yaml':continue
        target=path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture')
    manifest={'model':diarization.MODEL,'revision':'local','files':{name:diarization.hash_file(path/name) for name in diarization.FILES}}
    result=diarization.verify_model(path,metadata=manifest)
    assert result['revision']=='local'
    (path/'embedding/pytorch_model.bin').write_bytes(b'changed')
    with pytest.raises(ValueError,match='checksum'):diarization.verify_model(path,metadata=manifest)


def test_reanalysis_with_fewer_voices_keeps_valid_manual_assignments():
    doc=speakers.attach(document(),analysis())
    doc=subtitles.edit(doc,[{'id':'one','speaker':'speaker-1'}])
    reduced=analysis();reduced['speakers']=reduced['speakers'][:1]
    reduced['segments']=reduced['segments'][:1];reduced['exclusiveSegments']=reduced['exclusiveSegments'][:1]
    result=speakers.attach(doc,reduced)
    assert result['cues'][0]['speaker']=='speaker-1' and result['cues'][0]['speakerManual']
    assert result['cues'][0]['speakerCandidates']==['speaker-1']


def test_registered_local_model_uses_registry_hashes_in_preflight(tmp_path,monkeypatch):
    path=tmp_path/'local model';path.mkdir()
    (path/'config.yaml').write_text('pipeline:\n  name: pyannote.audio.pipelines.SpeakerDiarization\n  params:\n    embedding: $model/embedding\n    segmentation: $model/segmentation\n    plda: $model/plda\n')
    for name in diarization.FILES:
        if name=='config.yaml':continue
        target=path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture')
    monkeypatch.setattr(tool,'ROOT',tmp_path)
    actual_status=diarization.status
    def runtime_ready(root):
        info=actual_status(root);info['runtimeReady']=True;info['ready']=info['modelReady']
        info['state']='Installed' if info['ready'] else 'Missing'
        return info
    monkeypatch.setattr(diarization,'status',runtime_ready)
    def probe(self,ctx,parameters):
        assert parameters['task']=='probe'
        return {'ok':True,'result':{'durationSeconds':5}}
    monkeypatch.setattr(tool.ProcessWorker,'run',probe)
    media=tmp_path/'voice.wav';media.write_bytes(b'fixture')
    doc=document();doc['media']={'durationSeconds':25}
    source=tmp_path/'captions.json';source.write_text(json.dumps(doc),'utf-8')
    with tool.create_runtime(tmp_path/'jobs') as runtime:
        actor=runtime.authenticate(runtime.create_client('Local speaker model')['token']);sid=runtime.create_session(actor)['sessionId']
        job=runtime.wait(actor,runtime.submit(actor,sid,'register_diarization_model',{'path':str(path)})['jobId'],timeout=10)
        assert job['state']=='Completed',job
        assert not (path/'cytools-model.json').exists()
        job=runtime.wait(actor,runtime.submit(actor,sid,'diarize_subtitles',{'document':str(source),'media':str(media)})['jobId'],timeout=10)
        assert job['error']['code']=='MediaMismatch',job

        calls=[]
        def declared_timeline_worker(self,ctx,parameters):
            calls.append(parameters['task'])
            if parameters['task']=='probe':return {'ok':True,'result':{'durationSeconds':5}}
            if parameters['task']=='extract':
                assert parameters['filter']=='none'
                Path(parameters['destination']).write_bytes(b'wave fixture')
                return {'ok':True,'result':{}}
            assert parameters['task']=='infer'
            assert parameters['options']['num_speakers']==2 and parameters['options']['threads']==2
            assert parameters['options']['embedding_batch_size']==3
            Path(parameters['scratch']).write_bytes(b'float fixture')
            return {'ok':True,'result':analysis()}
        monkeypatch.setattr(tool.ProcessWorker,'run',declared_timeline_worker)
        doc['media']['durationSeconds']=5;source.write_text(json.dumps(doc),'utf-8')
        job=runtime.wait(actor,runtime.submit(actor,sid,'diarize_subtitles',{'document':str(source),'media':str(media),'speaker_count':2,'threads':2,'embedding_batch_size':3})['jobId'],timeout=10)
        assert job['state']=='Completed',job
        result=json.loads(Path(job['outputs']['document']).read_text('utf-8'))
        assert result['words']==doc['words'] and result['cues'][0]['text']==doc['cues'][0]['text']
        assert result['cues'][0]['speaker']=='speaker-1'
        assert calls==['probe','extract','infer']
        assert not list((Path(job['workspace'])/'intermediates').glob('*'))
