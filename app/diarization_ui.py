"""CyUI speaker controls. Imported by the desktop only."""
import json
import webbrowser
import cyui
import diarization
import nemotron
from ui_common import imgui, label, tr


OPTIONS=("diarization_engine","speaker_count","min_speakers","max_speakers","diarization_max_seconds","segmentation_batch_size","embedding_batch_size","speaker_labels",*nemotron.OPTION_KEYS)


def engine_selector(form,identifier='speaker-engine'):
    cyui.property(tr('Speaker engine'))
    engines=['community1','nemotron3'];names=['Community-1 (CPU)','NVIDIA Nemotron 3']
    changed,index=imgui.combo('##'+identifier,engines.index(form['diarization_engine']),[tr(n) for n in names])
    if changed:
        form['diarization_engine']=engines[index]
        if engines[index]=='nemotron3':
            form.update(speaker_count=0,min_speakers=1,max_speakers=16,segmentation_batch_size=1,embedding_batch_size=8)


def device_selector(form,identifier='nvidia-compute'):
    if form['diarization_engine']=='nemotron3':
        cyui.property(tr('NVIDIA compute'))
        values=['cpu','cuda'];_,index=imgui.combo('##'+identifier,values.index(form['nemotron_device']),['CPU','CUDA · GPU 0'])
        form['nemotron_device']=values[index]


def generation_options(form):
    nvidia=form['diarization_engine']=='nemotron3'
    if cyui.begin_properties('##speaker-options'):
        engine_selector(form);device_selector(form);nvidia=form['diarization_engine']=='nemotron3'
        if not nvidia:
            for key,title,lo,hi in [('speaker_count','Known speakers (0 = automatic)',0,32),('min_speakers','Minimum speakers',1,32),('max_speakers','Maximum speakers',1,32),('segmentation_batch_size','Segmentation batch size',1,16),('embedding_batch_size','Embedding batch size',1,64)]:
                cyui.property(tr(title))
                with cyui.scoped_disabled(bool(form['speaker_count']) and key in ('min_speakers','max_speakers')):
                    _,form[key]=imgui.slider_int('##'+key,form[key],lo,hi)
        else:
            cyui.property(tr('NVIDIA analysis mode'))
            values=['chunked','full'];changed,index=imgui.combo('##nvidia-mode',values.index(form['nemotron_mode']),[tr('Chunked with global voices'),tr('Full attention (up to 6 minutes)')])
            form['nemotron_mode']=values[index]
            if changed and values[index]=='full':
                form['nemotron_preset']='v3-offline'
                form.update({'nemotron_'+k:v for k,v in nemotron.GEOMETRY.items()})
            if form['nemotron_mode']=='chunked':
                cyui.property(tr('NVIDIA chunk preset'))
                values=['v3-offline','v3-streaming','custom'];changed,index=imgui.combo('##nvidia-preset',values.index(form['nemotron_preset']),[tr('Quality'),tr('Low latency'),tr('Custom')])
                form['nemotron_preset']=values[index]
                if changed and values[index]!='custom':form.update({'nemotron_'+k:v for k,v in nemotron.GEOMETRY.items()})
        cyui.property(tr('Diarization duration limit (seconds)'));_,form['diarization_max_seconds']=imgui.slider_int('##speaker-limit',form['diarization_max_seconds'],1,14400)
        cyui.property(tr('Include speaker names in subtitles'));_,form['speaker_labels']=imgui.checkbox('##speaker-labels',form['speaker_labels'])
        cyui.end_properties()
    if nvidia:
        cyui.text_dim(tr('NVIDIA estimates up to eight voices automatically. Phonon supplies the words and timestamps.'))
        if cyui.begin_section(label('NVIDIA segmentation and custom chunks'),False):
            if cyui.begin_properties('##nvidia-advanced'):
                for key,title in [('onset','Activation threshold'),('offset','Deactivation threshold'),('pad_onset','Start padding (seconds)'),('pad_offset','End padding (seconds)'),('min_duration_on','Minimum speech segment (seconds)'),('min_duration_off','Merge silence gaps below (seconds)')]:
                    cyui.property(tr(title));_,form['nemotron_'+key]=imgui.slider_float('##nvidia-'+key,form['nemotron_'+key],.001 if key in ('onset','offset') else 0.,1. if key in ('onset','offset') else 2.)
                if form['nemotron_mode']=='chunked' and form['nemotron_preset']=='custom':
                    for key,title in [('chunk','Chunk frames'),('right_context','Right context frames'),('left_context','Left context frames (-1 = default)'),('fifo','FIFO frames'),('spkcache','Speaker cache frames'),('update_period','Cache update frames')]:
                        cyui.property(tr(title));_,form['nemotron_'+key]=imgui.slider_int('##nvidia-'+key,form['nemotron_'+key],-1 if key=='left_context' else 0 if key in ('right_context','fifo') else 1,1024)
                cyui.end_properties()
            cyui.text_dim(tr('Custom geometry uses 80 ms frames. Invalid combinations are refused by the native engine.'))
            cyui.end_section()
    else:cyui.text_dim(tr('Community-1 runs locally on CPU. Voices are anonymous until you name them.'))


class Panel:
    def __init__(self,root):
        self.root=root;self.info=diarization.status(root);self.nvidia=nemotron.status(root);self.nvidia_accepted=False;self.nvidia_backend='cpu';self.nvidia_path='';self.runtime_accepted=False;self.model_accepted=False
        self.token='';self.local_path='';self.message='';self.document_path='';self.names={};self.show_labels=True
        self.rebuild=False;self.replace_manual=False

    def refresh(self):self.info=diarization.status(self.root);self.nvidia=nemotron.status(self.root)

    def ready(self,form):
        return self.nvidia['modelReady'] and self.nvidia[form['nemotron_device']+'Ready'] if form['diarization_engine']=='nemotron3' else self.info['ready']

    def nvidia_installation(self,submit,active):
        cyui.begin_card('##nvidia-speaker-install',tr('Speaker identification · NVIDIA Nemotron 3'))
        cyui.badge(tr('Installed' if self.nvidia['ready'] else 'Missing'),'success' if self.nvidia['ready'] else 'warning')
        cyui.text_dim(tr('Optional native engine. Model: about 107 MB; CPU runtime: 6 MB; CUDA runtime: 102 MB. Downloads are separate.'))
        cyui.text_dim('CPU / CUDA / '+tr('Model')+': '+' / '.join(tr('Installed' if self.nvidia[k] else 'Missing') for k in ('cpuReady','cudaReady','modelReady')))
        if cyui.button(label('NVIDIA model and license')):webbrowser.open(nemotron.CATALOG['model']['licenseUrl'])
        imgui.same_line()
        if cyui.button(label('NVIDIA runtime license')):webbrowser.open('https://github.com/NVIDIA/NeMo-Speech.cpp/blob/v0.2.0/LICENSE')
        if cyui.begin_properties('##nvidia-install-settings'):
            cyui.property(tr('Runtime to install'));values=['cpu','cuda'];_,index=imgui.combo('##install-nvidia-backend',values.index(self.nvidia_backend),['CPU','CUDA · NVIDIA']);self.nvidia_backend=values[index]
            cyui.property(tr('I reviewed and accept the NVIDIA model/runtime licenses'));_,self.nvidia_accepted=imgui.checkbox('##nvidia-license-acceptance',self.nvidia_accepted)
            cyui.end_properties()
        with cyui.scoped_disabled(active or not self.nvidia_accepted):
            if cyui.button(label('Install / repair NVIDIA runtime')):submit('install_nemotron_runtime',{'backend':self.nvidia_backend,'license_accepted':self.nvidia_accepted,'repair':True})
            imgui.same_line()
            if cyui.button(label('Download / repair NVIDIA model')):submit('install_nemotron_model',{'license_accepted':self.nvidia_accepted,'repair':True})
        with cyui.scoped_disabled(active):
            if cyui.button(label('Check NVIDIA compute')):submit('nemotron_diagnostics',{'backend':self.nvidia_backend})
            imgui.same_line()
            if cyui.button(label('Refresh NVIDIA installation')):submit('nemotron_status',{})
        if cyui.begin_section(label('Local NVIDIA GGUF'),False):
            if cyui.begin_properties('##local-nvidia-model'):
                cyui.property(tr('Model file'));_,self.nvidia_path=imgui.input_text('##nvidia-model-file',self.nvidia_path);cyui.end_properties()
            with cyui.scoped_disabled(active or not self.nvidia_path.strip()):
                if cyui.button(label('Register NVIDIA GGUF')):submit('register_nemotron_model',{'path':self.nvidia_path})
            cyui.end_section()
        cyui.text_dim(tr('CUDA is used only when selected and compatible. No system driver or Phonon library is changed.'))
        cyui.end_card()

    def installation(self,submit,active):
        cyui.begin_card('##speaker-install',tr('Speaker identification · Community-1'))
        cyui.badge(tr('Installed' if self.info['ready'] else 'Missing'),'success' if self.info['ready'] else 'warning')
        cyui.text_dim(tr('Optional download. Its CPU runtime is isolated from Phonon and is not included in the base ZIP.'))
        cyui.text_dim(tr('Model download: about 33 MB. The separate CPU runtime is substantially larger.'))
        cyui.text_dim(tr('Runtime / model')+': '+tr('Installed' if self.info['runtimeReady'] else 'Missing')+' / '+tr('Installed' if self.info['modelReady'] else 'Missing'))
        if cyui.button(label('Community-1 model and access conditions')):webbrowser.open(diarization.MODEL_URL)
        imgui.same_line()
        if cyui.button(label('Pyannote runtime license')):webbrowser.open('https://github.com/pyannote/pyannote-audio/blob/main/LICENSE')
        if cyui.begin_properties('##speaker-install-settings'):
            cyui.property(tr('I reviewed the diarization runtime licenses'))
            _,self.runtime_accepted=imgui.checkbox('##diar-runtime-license',self.runtime_accepted)
            cyui.property(tr('I accepted the Community-1 conditions on Hugging Face'))
            _,self.model_accepted=imgui.checkbox('##diar-model-license',self.model_accepted)
            cyui.end_properties()
        with cyui.scoped_disabled(active or not self.runtime_accepted):
            if cyui.button(label('Install / repair speaker runtime')):submit('install_diarization_runtime',{'license_accepted':True,'repair':True})
        imgui.same_line()
        with cyui.scoped_disabled(active or not self.model_accepted):
            if cyui.button(label('Download / repair Community-1')):submit('install_diarization_model',{'license_accepted':True,'repair':True})
        cyui.text_dim(tr('Credential available')+': '+tr('Yes' if self.info['credentialAvailable'] else 'No'))
        if cyui.begin_section(label('Hugging Face access')):
            cyui.text_dim(tr('Use an existing Hugging Face login or save a read token in Windows Credential Manager. Tokens never enter generation configurations or MCP parameters.'))
            if cyui.begin_properties('##speaker-credentials'):
                cyui.property(tr('Hugging Face access token'))
                _,self.token=imgui.input_text('Hugging Face access token',self.token,flags=imgui.InputTextFlags_.password)
                cyui.end_properties()
            with cyui.scoped_disabled(not self.token.strip()):
                if cyui.button(label('Save protected credential')):
                    try:diarization.save_credential(self.token);self.token='';self.refresh();cyui.notify(tr('Credential saved'),'success')
                    except Exception as exc:self.message=str(exc)
            imgui.same_line()
            if cyui.button(label('Token settings')):webbrowser.open('https://huggingface.co/settings/tokens')
            with cyui.scoped_disabled(active):
                if cyui.button(label('Check Community-1 access')):submit('check_diarization_access',{})
            cyui.end_section()
        if cyui.begin_section(label('Local Community-1 model'),False):
            if cyui.begin_properties('##local-community-model'):
                cyui.property(tr('Model directory'));_,self.local_path=imgui.input_text('##local-diar-model',self.local_path);cyui.end_properties()
            with cyui.scoped_disabled(active or not self.local_path.strip()):
                if cyui.button(label('Register Community-1 folder')):submit('register_diarization_model',{'path':self.local_path})
            cyui.end_section()
        with cyui.scoped_disabled(active):
            if cyui.button(label('Refresh speaker installation')):submit('diarization_status',{})
        if self.message:cyui.callout('warning',self.message)
        cyui.end_card()
        self.nvidia_installation(submit,active)

    def editor(self,document,path,media,form,submit,active):
        if not cyui.begin_section(label('Speakers')):return
        if cyui.begin_properties('##editor-speaker-engine'):
            engine_selector(form,'editor-speaker-engine');device_selector(form,'editor-nvidia-compute');cyui.end_properties()
        cyui.text_dim(tr('Changing speaker models creates new anonymous identities. Manual assignments require explicit replacement.'))
        if self.document_path!=path:
            self.document_path=path;self.names={s['id']:s['name'] for s in document.get('speakers',[])};self.show_labels=document.get('speakerLabels',True)
        if document.get('speakers'):
            if cyui.begin_properties('##speaker-names'):
                for speaker in document['speakers']:
                    cyui.property(speaker['id'])
                    _,self.names[speaker['id']]=imgui.input_text('##name-'+speaker['id'],self.names.get(speaker['id'],speaker['name']))
                cyui.property(tr('Include speaker names in subtitles'))
                _,self.show_labels=imgui.checkbox('##show-speakers',self.show_labels)
                cyui.end_properties()
            with cyui.scoped_disabled(active):
                if cyui.button(label('Save speaker names')):submit('rename_speakers',{'document':path,'names':dict(self.names),'show_labels':self.show_labels})
        else:cyui.text_dim(tr('No speaker analysis yet. Select the matching media, then identify its voices.'))
        if cyui.begin_section(label('Speaker analysis settings'),False):
            generation_options(form)
            _,self.rebuild=imgui.checkbox('Rebuild captions at speaker changes',self.rebuild)
            if self.rebuild:cyui.callout('warning',tr('Rebuild replaces manual speech text and layout using original word timings. Sound captions remain.'))
            _,self.replace_manual=imgui.checkbox('Replace manual speaker assignments',self.replace_manual)
            cyui.end_section()
        with cyui.scoped_disabled(active or not media or not self.ready(form)):
            if cyui.button(label('Identify speakers in this document')):
                keys=OPTIONS+('audio_stream','threads','max_chars','max_lines','max_duration','pause')
                submit('diarize_subtitles',{'media':media,'document':path,**{key:form[key] for key in keys},'rebuild':self.rebuild,'replace_manual':self.replace_manual})
        if not self.ready(form):cyui.callout('warning',tr('Install the selected speaker engine and model in Installation first.'))
        cyui.end_section()
