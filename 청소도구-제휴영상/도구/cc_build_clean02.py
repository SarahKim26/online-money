# 청소제휴 02편 캡컷 프로젝트 만들기 (음성 없음, 영상 ASMR 소리 그대로 + 짧은 자막 + 작은 배경음악)
# cc_build_1106.py 방식(템플릿 '태안 물결카라반' 스타일, 보조 파일은 '1105')
# usage: python -I cc_build_clean02.py [--dry]
import json, os, uuid, copy, time, shutil, sys, subprocess

ROOT = r'C:\Users\leade\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft'
ROOT_FWD = ROOT.replace('\\', '/')
TPL = os.path.join(ROOT, '\ud0dc\uc548 \ubb3c\uacb0\uce74\ub77c\ubc18')  # 태안 물결카라반
FRESH = os.path.join(ROOT, '1105')
SRC = r'C:\Users\leade\OneDrive\문서\0.1 인스타 쓰레드\인생이여행\청소제휴\02_둘째편\영상\캡컷소재'
SRC_FWD = SRC.replace('\\', '/')
BGM_NAME = '02_왈츠_Tinkerers Waltz_Gaugolon.mp3'
BGM = 'C:/Users/leade/OneDrive/문서/0.1 인스타 쓰레드/인생이여행/_배경음악/' + BGM_NAME
PROJ = '청소02 원룸 비포애프터'
OUT = os.path.join(ROOT, PROJ)

TITLE = '쓰레기 원룸이\n이렇게 바뀐다고?'
SUBTITLE = '6평 원룸 청소+셀프 인테리어'
HANDLE = '@sweet_home4949'
COVER = ('31_엔딩.mp4', 300000)   # 표지(맨 앞 2프레임) 장면
BGM_VOL = 0.2                      # 약 -14dB, 청소 소리(ASMR)가 주인공이라 여행 영상(-10dB)보다 작게
CLIP_VOL = 1.0                     # 영상 속 청소 소리 그대로

CLIPS = sorted(f for f in os.listdir(SRC) if f.endswith('.mp4'))
# 자막: (클립 번호(1부터), 클립 안 시작 비율, 문구) — 다음 자막 시작 또는 클립 끝까지 표시
CAPS = [
 (1, 0.0, '이사 갈 원룸'), (1, 0.5, '문 열었더니…'),
 (2, 0.0, '하…'), (2, 0.4, '어디서부터 치우지'),
 (8, 0.0, '진흙부터 싹'),
 (9, 0.0, '한 번 밀었더니'), (9, 0.5, '이 차이'),
 (13, 0.0, '기름때 싱크대'), (14, 0.0, '거품으로 문지르고'), (15, 0.0, '헹구면 반짝'),
 (19, 0.0, '뿌연 창문도'), (19, 0.5, '투명하게'),
 (21, 0.0, '곰팡이 벽지는'), (21, 0.5, '전부 뜯고'),
 (22, 0.0, '천장부터 새로'),
 (23, 0.0, '아이보리 벽지'),
 (24, 0.0, '하나씩 채우기'),
 (31, 0.0, '6평 원룸'), (31, 0.5, '완성'),
]
CAP_END_AT_CLIP_END = {8, 13, 14, 15, 22, 23, 24}  # 이 클립 자막은 클립 끝에서 사라짐(다음 클립으로 안 넘어감)

def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
def probe_us(p):
    return int(round(float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).stdout.strip()) * 1e6))
def nid():
    u = str(uuid.uuid4()).split('-')
    return f'{u[0].upper()}-{u[1].upper()}-{u[2].lower()}-{u[3].upper()}-{u[4].upper()}'
def F(f):
    return int(round(f * 1000000 / 30))
def tr(s, d):
    return {'start': int(s), 'duration': int(d)}

VDUR = {c: probe_us(os.path.join(SRC, c)) for c in CLIPS}
BGM_DUR = probe_us(BGM)

# clip placement in frames (30fps), video starts after 2-frame cover
starts_f = []
pos = 2
for c in CLIPS:
    n = int(VDUR[c] * 30 // 1000000)  # whole frames inside the file
    starts_f.append((pos, pos + n))
    pos += n
END_F = pos

if os.path.exists(OUT) and '--dry' not in sys.argv:
    sys.exit('output exists: ' + OUT)

tpl = json.load(open(os.path.join(TPL, 'draft_content.json'), encoding='utf-8'))
idx = {}
for k, v in tpl['materials'].items():
    if isinstance(v, list):
        for it in v:
            if isinstance(it, dict) and 'id' in it:
                idx[it['id']] = (k, it)
T = tpl['tracks']
seg_video_t, seg_title_t, seg_sub_t, seg_handle_t, seg_cap_t, seg_audio_t = [T[i]['segments'][0] for i in range(6)]
new_mats = {k: [] for k in ['videos', 'audios', 'texts', 'canvases', 'beats', 'material_animations', 'placeholder_infos',
                            'speeds', 'sound_channel_mappings', 'material_colors', 'vocal_separations', 'audio_fades']}

def clone_extras(seg_t):
    refs = []
    for r in seg_t['extra_material_refs']:
        kind, it = idx[r]
        n = copy.deepcopy(it); n['id'] = nid()
        if kind == 'speeds':
            n['speed'] = 1.0
        new_mats[kind].append(n); refs.append(n['id'])
    return refs

video_tpl_mat = idx[seg_video_t['material_id']][1]
def make_video(fname, ts_f, te_f, src_us, vol):
    mat = copy.deepcopy(video_tpl_mat)
    mat['id'] = nid(); mat['path'] = SRC_FWD + '/' + fname; mat['material_name'] = fname
    mat['duration'] = VDUR[fname]; mat['width'] = 1080; mat['height'] = 1920; mat['has_audio'] = True
    mat['local_material_id'] = ''; mat['origin_material_id'] = ''
    new_mats['videos'].append(mat)
    seg = copy.deepcopy(seg_video_t)
    seg['id'] = nid(); seg['material_id'] = mat['id']
    ts, te = F(ts_f), F(te_f)
    seg['target_timerange'] = tr(ts, te - ts)
    seg['source_timerange'] = tr(src_us, te - ts)
    seg['speed'] = 1.0
    seg['volume'] = vol; seg['last_nonzero_volume'] = 1.0
    seg['extra_material_refs'] = clone_extras(seg_video_t)
    return seg

video_segs = [make_video(COVER[0], 0, 2, COVER[1], 0.0)]
for c, (a, b) in zip(CLIPS, starts_f):
    video_segs.append(make_video(c, a, b, 0, CLIP_VOL))

# BGM
audio_tpl_mat = idx[seg_audio_t['material_id']][1]
bmat = copy.deepcopy(audio_tpl_mat)
bmat['id'] = nid(); bmat['path'] = BGM; bmat['name'] = BGM_NAME; bmat['duration'] = BGM_DUR; bmat['local_material_id'] = ''
new_mats['audios'].append(bmat)
bseg = copy.deepcopy(seg_audio_t)
bseg['id'] = nid(); bseg['material_id'] = bmat['id']
bseg['target_timerange'] = tr(F(2), F(END_F) - F(2))
bseg['source_timerange'] = tr(0, F(END_F) - F(2))
bseg['volume'] = BGM_VOL; bseg['last_nonzero_volume'] = BGM_VOL
fade = {'id': nid(), 'type': 'audio_fade', 'fade_type': 0, 'fade_in_duration': 0, 'fade_out_duration': 1000000}
new_mats['audio_fades'].append(fade)
bseg['extra_material_refs'] = clone_extras(seg_audio_t) + [fade['id']]

def make_text(seg_t, text, s_us, e_us, y=None, render_index=None, tri=None):
    mat = copy.deepcopy(idx[seg_t['material_id']][1])
    mat['id'] = nid()
    c = json.loads(mat['content']); c['text'] = text
    for st in c['styles']:
        st['range'] = [0, len(text)]
    mat['content'] = json.dumps(c, ensure_ascii=False, separators=(',', ':'))
    try:
        bc = json.loads(mat['base_content']); bc['text'] = text
        for st in bc.get('styles', []):
            st['range'] = [0, len(text)]
        mat['base_content'] = json.dumps(bc, ensure_ascii=False, separators=(',', ':'))
    except Exception:
        mat['base_content'] = ''
    mat['recognize_text'] = text; mat['translate_original_text'] = text; mat['recognize_task_id'] = ''
    mat['words'] = {'start_time': [], 'end_time': [], 'text': []}
    mat['current_words'] = {'start_time': [], 'end_time': [], 'text': []}
    new_mats['texts'].append(mat)
    seg = copy.deepcopy(seg_t)
    seg['id'] = nid(); seg['material_id'] = mat['id']
    seg['target_timerange'] = tr(s_us, e_us - s_us)
    if y is not None:
        seg['clip']['transform']['y'] = y
    if render_index is not None:
        seg['render_index'] = render_index
    if tri is not None:
        seg['track_render_index'] = tri
    seg['extra_material_refs'] = clone_extras(seg_t)
    return seg

title = make_text(seg_title_t, TITLE, 0, F(2))
subt = make_text(seg_sub_t, SUBTITLE, 0, F(2))
handle = make_text(seg_handle_t, HANDLE, F(2), F(END_F), y=-0.625)

cap_plan = []
for i, (ci, frac, txt) in enumerate(CAPS):
    a, b = starts_f[ci - 1]
    s = a + int(round((b - a) * frac))
    if i + 1 < len(CAPS) and CAPS[i + 1][0] == ci:
        e = starts_f[ci - 1][0] + int(round((b - a) * CAPS[i + 1][1]))
    elif ci in CAP_END_AT_CLIP_END or i + 1 == len(CAPS):
        e = b
    else:
        e = b  # 자막은 그 클립 안에서만
    cap_plan.append((txt, s, e))
cap_segs = [make_text(seg_cap_t, t, F(s), F(e), y=0.453125, render_index=14004, tri=4) for t, s, e in cap_plan]

d = copy.deepcopy(tpl)
TL_ID = nid()
d['id'] = TL_ID; d['duration'] = F(END_F); d['name'] = ''
d['config']['subtitle_taskinfo'] = []; d['config']['subtitle_recognition_id'] = ''
d['extra_info']['subtitle_fragment_info_list'] = []
d['relationships'] = []
for k, v in new_mats.items():
    d['materials'][k] = v
def track(t_tpl, segs):
    t = copy.deepcopy(t_tpl); t['id'] = nid(); t['segments'] = segs
    return t
d['tracks'] = [track(T[0], video_segs), track(T[1], [title]), track(T[2], [subt]), track(T[3], [handle]),
               track(T[4], cap_segs), track(T[5], [bseg])]

summary = {'out': OUT, 'duration_s': round(F(END_F) / 1e6, 2),
           'clips': [(c, round(F(a) / 1e6, 2), round(F(b) / 1e6, 2)) for c, (a, b) in zip(CLIPS, starts_f)],
           'caps': [(t, round(F(s) / 1e6, 2), round(F(e) / 1e6, 2)) for t, s, e in cap_plan]}
if '--dry' in sys.argv:
    print(json.dumps(summary, ensure_ascii=False, indent=0)); sys.exit(0)

now_s = int(time.time()); now_us = int(time.time() * 1e6)
DRAFT_ID = nid(); PROJ_ID = nid()
os.makedirs(os.path.join(OUT, 'common_attachment'))
TLD = os.path.join(OUT, 'Timelines', TL_ID)
os.makedirs(os.path.join(TLD, 'common_attachment'))
def wj(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
for p in [os.path.join(OUT, 'draft_content.json'), os.path.join(OUT, 'template-2.tmp'),
          os.path.join(TLD, 'draft_content.json'), os.path.join(TLD, 'template-2.tmp')]:
    wj(p, d)
FRESH_TL = os.path.join(FRESH, 'Timelines', '3A9FAE08-8589-4ba1-BC54-81D27368AE40')
for rel in ['attachment_pc_common.json', 'draft_agency_config.json', 'performance_opt_info.json',
            'common_attachment/attachment_id_mapping.json', 'common_attachment/attachment_pc_timeline.json']:
    shutil.copyfile(os.path.join(FRESH, rel), os.path.join(OUT, rel))
for rel in ['attachment_editing.json', 'attachment_pc_common.json', 'template.tmp',
            'common_attachment/attachment_action_scene.json', 'common_attachment/attachment_gen_ai_info.json',
            'common_attachment/attachment_id_mapping.json', 'common_attachment/attachment_pc_timeline.json',
            'common_attachment/attachment_script_video.json']:
    shutil.copyfile(os.path.join(FRESH_TL, rel), os.path.join(TLD, rel))
open(os.path.join(OUT, 'draft_biz_config.json'), 'w').close()
wj(os.path.join(OUT, 'key_value.json'), {})
wj(os.path.join(OUT, 'timeline_layout.json'), {"dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [TL_ID], "timelineNames": ["Timeline 01"]}], "layoutOrientation": 1})
wj(os.path.join(OUT, 'Timelines', 'project.json'), {"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": False, "use_float_render": False}, "create_time": now_us, "id": PROJ_ID, "main_timeline_id": TL_ID, "timelines": [{"create_time": now_us, "id": TL_ID, "is_marked_delete": False, "name": "Timeline 01", "update_time": now_us}], "update_time": now_us, "version": 0})
with open(os.path.join(OUT, 'draft_settings'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(f'[General]\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=0\nreal_edit_keys=0\n')
meta = json.load(open(os.path.join(FRESH, 'draft_meta_info.json'), encoding='utf-8'))
meta.update({'draft_fold_path': ROOT_FWD + '/' + PROJ, 'draft_id': DRAFT_ID, 'draft_name': PROJ, 'draft_cover': 'draft_cover.jpg',
             'draft_root_path': ROOT, 'tm_draft_create': now_us, 'tm_draft_modified': now_us, 'tm_duration': F(END_F),
             'draft_new_version': ''})
def dm_entry(path, dur, metetype, typ, w, h):
    return {"ai_group_type": "", "create_time": now_s, "duration": dur, "enter_from": 0, "extra_info": path.split('/')[-1],
            "file_Path": path, "height": h, "id": nid(), "import_time": now_s, "import_time_ms": now_us // 1000,
            "item_source": 1, "material_color_tag": "", "md5": "", "metetype": metetype,
            "roughcut_time_range": {"duration": dur, "start": 0}, "sub_time_range": {"duration": -1, "start": -1},
            "type": typ, "width": w}
for g in meta['draft_materials']:
    if g['type'] == 0:
        g['value'] = [dm_entry(SRC_FWD + '/' + c, VDUR[c], 'video', 0, 1080, 1920) for c in CLIPS]
    elif g['type'] == 1:
        g['value'] = [dm_entry(BGM, BGM_DUR, 'extract_music', 1, 0, 0)]
wj(os.path.join(OUT, 'draft_meta_info.json'), meta)
for cov in [os.path.join(OUT, 'draft_cover.jpg'), os.path.join(TLD, 'draft_cover.jpg')]:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(COVER[1] / 1e6), '-i', os.path.join(SRC, COVER[0]),
                    '-frames:v', '1', '-vf', 'scale=1080:1920', '-q:v', '2', cov], check=True)
summary.update({'draft_id': DRAFT_ID, 'timeline_id': TL_ID})
json.dump(summary, open(os.path.join(OUT, '_build_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('OK', DRAFT_ID, TL_ID)
