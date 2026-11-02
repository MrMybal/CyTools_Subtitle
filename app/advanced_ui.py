"""Complete operation access for standalone users; no UI imports in the runtime."""
import json
from pathlib import Path
import sys
from cyui_modules.code import CodeEditor, CodeDocument, CodeViewState, code_viewer
from concurrent.futures import ThreadPoolExecutor

class Panel:
    def __init__(self,runtime,principal=None):
        self.runtime=runtime;self.index=0;self.drafts={};self.job=None;self.message='';self.frames=0
        self.test='--ui-test-advanced' in sys.argv;self.future=None;self.executor=ThreadPoolExecutor(max_workers=1)
        self.editors={};self.code_views={};self.selectable_json={}
        if runtime is not None:
            from cytools_core.transports.api import LocalClient
            from model_options_ui import submit_exact
            self.submit=lambda *args,**kwargs:submit_exact(runtime,*args,**kwargs)
            self.principal=principal or runtime.authenticate(runtime.create_client('Standalone advanced')['token'])
            self.client=LocalClient(runtime,self.principal);self.session=runtime.create_session(self.principal, temporary=False)['sessionId']
            from ui_common import journal
            journal.bind(runtime,self.principal)
    def state(self):
        operation=self.runtime.descriptor['operations'][self.index]
        if operation['id'] not in self.drafts:
            defaults={k:v['default'] for k,v in operation['inputSchema'].get('properties',{}).items() if 'default' in v}
            self.drafts[operation['id']]={'text':json.dumps(defaults,indent=2),'backend':'','model':'','priority':3,'queue':'','execution':'','path':''}
        return operation,self.drafts[operation['id']]
    def payload(self):
        operation,state=self.state()
        from cytools_core import validate_parameters
        return validate_parameters(json.loads(state['text']),operation['inputSchema'])
    def restore(self,value):
        self.index=next(i for i,o in enumerate(self.runtime.descriptor['operations']) if o['id']==value['operationId'])
        _,state=self.state();state.update(text=json.dumps(value['parameters'],indent=2,ensure_ascii=False),backend=value.get('backendId',''),model=value.get('modelId',''))
        for key in ('priority','queue','execution'):
            if key in value.get('uiState',{}).get('invocation',{}):state[key]=value['uiState']['invocation'][key]
    def draw_json(self,identifier,text,height):
        import cyui
        from ui_common import raw,label
        if identifier not in self.code_views:
            editor=CodeEditor('', 'json');editor.read_only=True;editor.preview=False
            self.code_views[identifier]=(CodeDocument('', 'json'),CodeViewState(),editor)
        document,state,editor=self.code_views[identifier]
        _,self.selectable_json[identifier]=raw().checkbox(label('Selectable JSON text##'+identifier),self.selectable_json.get(identifier,False))
        if self.selectable_json[identifier]:
            if editor.text!=text:editor.set_text(text)
            editor.draw(identifier+'##selectable',(-1,cyui.dp(height)))
        else:
            document.set_text(text,'json');code_viewer(identifier,state,document,(0,cyui.dp(height)))

    def draw_tab(self):
        from ui_common import raw,label
        ui=raw();opened,_=ui.begin_tab_item(label('Advanced operations'),flags=ui.TabItemFlags_.set_selected if self.test else 0)
        if opened:
            try:self.draw_panel()
            finally:ui.end_tab_item()
    def draw_panel(self):
        from ui_common import raw,label,tr,ROOT,current_recipe
        import cyui
        ui=raw()
        try:
            self.frames+=1
            if self.runtime is None:ui.text_wrapped(tr('Runtime unavailable'));return
            if self.future and self.future.done():
                try:self.message=json.dumps(self.future.result(),indent=2,ensure_ascii=False)
                except Exception as exc:self.message=str(exc)
                self.future=None
            if self.job:self.job=self.runtime.get_job(self.principal,self.job['jobId'])
            if cyui.begin_properties('##property-Operation'):
                cyui.property(tr('Operation'))
                _,self.index=ui.combo('##Operation',self.index,[o['id'] for o in self.runtime.descriptor['operations']])
                cyui.end_properties()
            operation,state=self.state()
            ui.text_wrapped(tr('All declared parameters are available here. This JSON takes precedence over the simplified form and model preferences.'))
            ui.text_wrapped(operation['description'])
            if ui.button(label('Copy operation contract')):ui.set_clipboard_text(json.dumps(operation,indent=2,ensure_ascii=False))
            ui.same_line()
            if ui.button(label('Import current form')):self.restore(current_recipe());operation,state=self.state()
            if ui.collapsing_header(label('Full input and output schemas')):
                self.draw_json('##contract',json.dumps(operation,indent=2,ensure_ascii=False),210)
            if operation['id'] not in self.editors:self.editors[operation['id']]=CodeEditor(state['text'],'json')
            editor=self.editors[operation['id']]
            if editor.text!=state['text']:editor.set_text(state['text'])
            _,editor.preview=ui.checkbox(label('JSON syntax preview'),editor.preview)
            editor.draw('##parameters-json-'+operation['id'],(-1,cyui.dp(290 if editor.preview else 200)));state['text']=editor.text
            if cyui.begin_properties('##property-Backend ID'):
                cyui.property(tr('Backend ID'))
                _,state['backend']=ui.input_text('##Backend ID',state['backend'])
                cyui.end_properties()
            if cyui.begin_properties('##property-Model ID'):
                cyui.property(tr('Model ID'))
                _,state['model']=ui.input_text('##Model ID',state['model'])
                cyui.end_properties()
            priorities=['Interactive','Critical','High','Normal','Background','Low']
            if cyui.begin_properties('##property-Priority'):
                cyui.property(tr('Priority'))
                _,state['priority']=ui.combo('##Priority',state['priority'],priorities)
                cyui.end_properties()
            if cyui.begin_properties('##property-Queue timeout (seconds, empty = default)'):
                cyui.property(tr('Queue timeout (seconds, empty = default)'))
                _,state['queue']=ui.input_text('##Queue timeout (seconds, empty = default)',state['queue'])
                cyui.end_properties()
            if cyui.begin_properties('##property-Execution timeout (seconds, empty = default)'):
                cyui.property(tr('Execution timeout (seconds, empty = default)'))
                _,state['execution']=ui.input_text('##Execution timeout (seconds, empty = default)',state['execution'])
                cyui.end_properties()
            if ui.button(label('Validate and estimate')) and self.future is None:
                self.future=self.executor.submit(self.client.call,'CanRun',operationId=operation['id'],parameters=self.payload(),backendId=state['backend'],modelId=state['model'])
            ui.same_line()
            active=self.job and self.job['state'] not in ('Completed','Cancelled','Failed')
            ui.begin_disabled(bool(active))
            try:
                if cyui.primary_button(label('Run exact parameters')):
                    options={key:float(state[field]) for key,field in (('queue_timeout','queue'),('execution_timeout','execution')) if state[field].strip()}
                    self.job=self.submit(self.principal,self.session,operation['id'],self.payload(),backend_id=state['backend'],model_id=state['model'],priority=priorities[state['priority']],**options)
                    self.message=json.dumps(self.job,indent=2,ensure_ascii=False)
            finally:ui.end_disabled()
            if active:
                ui.same_line()
                if ui.button(label('Cancel')):self.runtime.cancel(self.principal,self.job['jobId'])
            if cyui.begin_properties('##property-Configuration path'):
                cyui.property(tr('Configuration path'))
                _,state['path']=ui.input_text('##Configuration path',state['path'])
                cyui.end_properties()
            if ui.button(label('Save exact configuration')):
                from generation_config import recipe,save
                path=Path(state['path']) if state['path'] else ROOT/'data/configurations'/(operation['id']+'-advanced.json')
                save(path,recipe(self.runtime.descriptor,operation['id'],self.payload(),backend=state['backend'],model=state['model'],ui_state={'invocation':{k:state[k] for k in ('priority','queue','execution')}}))
                state['path']=str(path);self.message=str(path)
            ui.same_line()
            if ui.button(label('Load configuration')):
                from generation_config import load
                self.restore(load(state['path'],self.runtime.descriptor))
            if self.job:
                ui.text(self.job['state'])
                if ui.button(label('Copy job and outputs')):ui.set_clipboard_text(json.dumps(self.job,indent=2,ensure_ascii=False))
                self.draw_json('##job',json.dumps(self.job,indent=2,ensure_ascii=False),180)
            if self.message:
                if cyui.button(label('Copy result')):ui.set_clipboard_text(self.message)
                self.draw_json('##result',self.message,160)
        except Exception as exc:self.message=str(exc)


    def close(self):
        self.executor.shutdown(wait=True,cancel_futures=True)
        if self.runtime is not None:
            try:self.runtime.close_session(self.principal,self.session)
            except Exception:pass
