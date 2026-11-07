# 청소제휴 02편: Flow 원본(720/1080) -> 캡컷 소재(1080x1920, 30fps, 배속, 음량 맞춤)
# usage: python -I clean02_prep.py
import subprocess, os, json
BASE = r'C:\Users\leade\OneDrive\문서\0.1 인스타 쓰레드\인생이여행\청소제휴\02_둘째편\영상'
import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, '캡컷소재')  # 캡컷소재
os.makedirs(OUT, exist_ok=True)
R = '원본_720검수'
# (출력이름, 원본, 시작초, 끝초(None=끝), 배속)
PLAN = [
 ('01_비명', r'원본\C01_비명.mp4', 0, None, 1.2),
 ('02_한숨_장갑', r'원본\C02_한숨_장갑.mp4', 0, None, 1.5),
 ('03_왼쪽쓰레기', R + r'\C03_왼쪽쓰레기.mp4', 0, None, 2.5),
 ('04_오른쪽쓰레기', R + r'\C04_오른쪽쓰레기.mp4', 0, None, 2.5),
 ('05_봉투나르기', R + r'\C05_봉투나르기.mp4', 0, None, 2.5),
 ('06_블라인드', R + r'\C06_블라인드.mp4', 0, None, 2.5),
 ('07_매트리스의자', R + r'\C07_매트리스의자.mp4', 0, None, 2.5),
 ('08_진흙밀기', R + r'\C08_진흙밀기.mp4', 0, None, 2.5),
 ('09_줌인_바닥한줄', R + r'\C09_줌인_바닥한줄.mp4', 0, None, 1.5),
 ('10_바닥앞쪽', R + r'\C10_바닥앞쪽.mp4', 0, None, 2.5),
 ('11_바닥뒤쪽', R + r'\C11_바닥뒤쪽.mp4', 0, None, 2.5),
 ('12_창가얼룩', R + r'\C11b_창가얼룩.mp4', 0, None, 2.5),
 ('13_줌인_싱크거품', R + r'\C12_줌인_싱크거품.mp4', 0, None, 1.5),
 ('14_줌인_싱크브러시', R + r'\C13_줌인_싱크브러시.mp4', 0, None, 1.5),
 ('15_줌인_싱크헹굼', R + r'\C14_줌인_싱크헹굼.mp4', 0, None, 1.5),
 ('16_수납장타일', R + r'\C15_수납장타일_넓게.mp4', 0, None, 2.5),
 ('17_줌인_타일', R + r'\C16_줌인_타일.mp4', 0, None, 1.5),
 ('18_창문_스프레이', R + r'\C17_창문_넓게.mp4', 0, 2.0, 2.0),
 ('19_줌인_창문', R + r'\C18_줌인_창문.mp4', 0, None, 1.5),
 ('20_창문_투명', R + r'\C17_창문_넓게.mp4', 2.0, None, 2.0),
 ('21_벽지뜯기', R + r'\C19_벽지뜯기.mp4', 0, None, 2.5),
 ('22_천장', r'편집\C20_천장_3단계_720.mp4', 0, None, 1.5),
 ('23_벽지바르기', R + r'\C21_벽지바르기.mp4', 0, None, 2.5),
 ('24_침대', R + r'\C22_침대.mp4', 0, None, 2.5),
 ('25_소파TV', R + r'\C23_소파TV_재생성.mp4', 0, None, 2.5),
 ('26_커튼', R + r'\C24_커튼.mp4', 0, None, 2.5),
 ('27_주방소품', R + r'\C25_주방소품.mp4', 0, None, 2.5),
 ('28_러그나무', R + r'\C26_러그나무.mp4', 0, None, 2.5),
 ('29_포스터', R + r'\C27_포스터거울.mp4', 0, 1.2, 1.5),
 ('30_거울무드등', R + r'\C27b_거울무드등.mp4', 0, None, 2.0),
 ('31_엔딩', R + r'\C28_엔딩.mp4', 0, None, 1.0),
]

def dur(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                       capture_output=True, text=True).stdout
    return float(o.strip())

info = []
for name, src, a, b, sp in PLAN:
    p = os.path.join(BASE, src)
    d = dur(p)
    b = d if b is None else min(b, d)
    out = os.path.join(OUT, name + '.mp4')
    vf = f'trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p'
    af = f'atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={sp},loudnorm=I=-18:TP=-2:LRA=11,aresample=48000'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-filter_complex', f'[0:v]{vf}[v];[0:a]{af}[a]',
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', out], check=True)
    info.append((name, round(dur(out), 3), sp))
    print(name, round(dur(out), 3))
print('TOTAL', round(sum(x[1] for x in info), 2))
json.dump(info, open(os.path.join(OUT, '_소재목록.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
