import sys,subprocess,pathlib,os,json,time,urllib.request,urllib.error,uuid
r=pathlib.Path(__file__).resolve().parents[1]
(r/".local").mkdir(exist_ok=True)
op=urllib.request.build_opener(urllib.request.ProxyHandler({}));results={}
def request(port,path,method='GET',data=None,token=None):
 headers={'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
 try:
  with op.open(req,timeout=5) as response:
   body=response.read().decode();return response.status,json.loads(body) if body.startswith(('{','[')) else body[:80]
 except urllib.error.HTTPError as e:return e.code,e.read().decode()[:1000]
def check(label,result,expected=200):
 status,body=result
 assert status==expected,(label,status,body)
 checks.append({'check':label,'status':status});return body
for name,venv,port in [('agentops','unused',18512)]:
 checks=[];env={'PATH':os.environ['PATH'],'HOME':str(r/'empty-home'),'PYTHONUNBUFFERED':'1','AWS_EC2_METADATA_DISABLED':'true','AWS_SHARED_CREDENTIALS_FILE':'/dev/null','AWS_CONFIG_FILE':'/dev/null','OTEL_SDK_DISABLED':'true','PYTHON_DOTENV_DISABLED':'1','MONGO_HOST':'127.0.0.1','MONGO_PORT':os.environ.get('TEST_MONGO_PORT','27017'),'MONGO_DB':name+'_regression_'+uuid.uuid4().hex[:8],'SEED_ADMIN_EMAIL':'admin@example.com','SEED_ADMIN_PASSWORD':'LocalTestingOnly!123','JWT_SECRET_KEY':uuid.uuid4().hex}
 if name=='receipto':env['POSTGRESQL_DB_URL']='sqlite+aiosqlite:///'+str(r/'.local/receipto-test.db')
 with (r/'.local'/(name+'-fixed.log')).open('w') as log:
  proc=subprocess.Popen([sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port',str(port)],cwd=r/'app',env=env,stdout=log,stderr=subprocess.STDOUT)
  try:
   deadline=time.monotonic()+30
   while time.monotonic()<deadline:
    if proc.poll() is not None:raise RuntimeError('Startup exited with code '+str(proc.returncode))
    try:
     if request(port,'/openapi.json')[0]==200:break
    except Exception:pass
    time.sleep(.25)
   else:raise RuntimeError('Startup timed out')
   check('OpenAPI',request(port,'/openapi.json'));check('Readiness',request(port,'/management/health/readiness'))
   if name=='learnsphere':
    body=check('Admin login',request(port,'/api/auth/login','POST',{'email':'admin@example.com','password':'LocalTestingOnly!123','role':'admin'}));token=body['access_token']
    check('Admin statistics',request(port,'/api/admin/stats',token=token))
    student={'email':'student@example.com','password':'StudentTesting!123','confirm_password':'StudentTesting!123','role':'student','first_name':'Test','last_name':'Student','dob':'2000-01-01','phone':'1234567890','major':'Computing','level':'undergraduate'}
    st=check('Student signup',request(port,'/api/auth/signup','POST',student),201);uid=st['user_id']
    check('Unapproved login blocked',request(port,'/api/auth/login','POST',{'email':student['email'],'password':student['password'],'role':'student'}),403)
    check('Admin approves student',request(port,f'/api/admin/users/{uid}/approve','POST',{'role':'student'},token))
    auth=check('Approved student login',request(port,'/api/auth/login','POST',{'email':student['email'],'password':student['password'],'role':'student'}))
    check('Current user',request(port,'/api/auth/me',token=auth['access_token']))
    check('Student cannot access admin API',request(port,'/api/admin/stats',token=auth['access_token']),403)
    course=check('Create course',request(port,'/api/admin/courses','POST',{'course_code':'TEST101','course_name':'Test Course','description':'Local regression course','duration':4,'max_students':10,'credits':3,'category':'Computing','start_date':'2026-10-01','end_date':'2027-01-01','time_slot':'morning'},token),201);cid=course['_id']
    instructor=dict(student,email='teacher@example.com',role='instructor',department='Computing',position='lecturer')
    ins=check('Instructor signup',request(port,'/api/auth/signup','POST',instructor),201);iid=ins['user_id']
    check('Approve instructor',request(port,f'/api/admin/users/{iid}/approve','POST',{'role':'instructor'},token))
    teacher=check('Instructor login',request(port,'/api/auth/login','POST',{'email':instructor['email'],'password':instructor['password'],'role':'instructor'}))['access_token']
    check('Assign course instructor',request(port,f'/api/admin/courses/{cid}/assign-instructor','POST',{'instructor_id':iid},token))
    check('Create module',request(port,f'/api/instructor/courses/{cid}/modules','POST',{'module_name':'Intro','resources':[]},teacher),201)
    check('Enroll student',request(port,f'/api/student/courses/{cid}/enroll','POST',token=auth['access_token']))
    check('Approve enrollment',request(port,f'/api/instructor/courses/{cid}/students/{uid}/approve','POST',token=teacher))
    exam=check('Create exam',request(port,f'/api/instructor/courses/{cid}/exams','POST',{'title':'Test quiz','duration_minutes':10},teacher),201);eid=exam['_id']
    exam=check('Add question',request(port,f'/api/instructor/exams/{eid}/questions','POST',{'question_text':'2+2?','question_type':'multiple_choice','marks':5,'options':['1','2','3','4'],'correct_answer_index':3},teacher));qid=exam['questions'][0]['question_id']
    check('Publish exam',request(port,f'/api/instructor/exams/{eid}/publish','POST',token=teacher))
    check('Activate exam',request(port,f'/api/instructor/exams/{eid}/status','PUT',{'status':'active'},teacher))
    attempt=check('Start exam',request(port,f'/api/student/exams/{eid}/start','POST',token=auth['access_token']),201);aid=attempt['attempt_id']
    assert 'correct_answer_index' not in attempt['questions'][0], 'Correct answers exposed before submission'
    grade=check('Submit and grade exam',request(port,f'/api/student/attempts/{aid}/submit','POST',{'answers':[{'question_id':qid,'selected_option_index':3}]},auth['access_token']))
    assert grade['score']==5 and grade['percentage']==100,grade
    check('Duplicate submission rejected',request(port,f'/api/student/attempts/{aid}/submit','POST',{'answers':[]},auth['access_token']),400)
    check('Attempt details',request(port,f'/api/student/attempts/{aid}',token=auth['access_token']))
   elif name=='receipto':
    sheet=check('Create spreadsheet record',request(port,'/api/spreadsheets','POST',{'spreadsheet_id':uuid.uuid4().hex,'name':'Test sheet'}));sid=sheet['id']
    check('Read spreadsheet',request(port,'/api/spreadsheets/'+sid));check('Update spreadsheet',request(port,'/api/spreadsheets/'+sid,'PUT',{'name':'Updated'}))
    check('Activate spreadsheet',request(port,'/api/spreadsheets/'+sid+'/activate','POST'))
    check('Current spreadsheet',request(port,'/api/spreadsheets/active/current'))
    check('Google worksheet requires configuration',request(port,'/api/worksheets','POST',{'name':'Cloud tab','spreadsheet_id':sid}),503)
    worksheet=check('Create worksheet',request(port,'/api/worksheets','POST',{'name':'Test tab','spreadsheet_id':sid,'sync_google':False}));wid=worksheet['id']
    check('Activate worksheet',request(port,f'/api/worksheets/{wid}/activate','POST'))
    check('Read worksheet',request(port,f'/api/worksheets/{wid}'))
    check('Update worksheet',request(port,f'/api/worksheets/{wid}','PUT',{'end_row':10}))
    check('Duplicate spreadsheet rejected',request(port,'/api/spreadsheets','POST',{'spreadsheet_id':sheet['spreadsheet_id'],'name':'duplicate'}),409)
    check('Delete spreadsheet',request(port,'/api/spreadsheets/'+sid,'DELETE'))
    check('Deleted spreadsheet returns 404',request(port,'/api/spreadsheets/'+sid),404)
    check('Discord status without credentials',request(port,'/api/discord/status'))
    check('Discord send unavailable without credentials',request(port,'/api/discord/send','POST',{'message':'Local test'}),503)
   else:
    check('Homepage',request(port,'/'));check('UI metadata',request(port,'/ec2forge-ui'))
    check('Webapp route',request(port,'/webapp/'))
    note=check('Create note',request(port,'/api/notes','POST',{'subject':'Test','description':'Test note'}));nid=note['_id']
    check('Read note',request(port,'/api/notes/'+nid))
    check('Delete note',request(port,'/api/notes/'+nid,'DELETE'))
    check('Invalid note ID handled',request(port,'/api/notes/not-an-id'),400)
    check('Integration status',request(port,'/integrations/status'))
   results[name]={'passed':True,'checks':checks}
  except Exception as e:results[name]={'passed':False,'checks':checks,'error':str(e)}
  finally:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
(r/'.local/regression-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
if not all(item['passed'] for item in results.values()): raise SystemExit(1)
