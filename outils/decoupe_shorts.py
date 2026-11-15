# Découpe une vidéo longue (horizontale) en Shorts verticaux 1080x1920 (fond flou + vidéo centrée), 59 s max chacun.
# Usage (dans le workbench) : exec(requests.get(RAW_URL).text) puis
#   decouper('/mnt/files/video.mp4', [(12, 50, 'hdv19-defense'), (80, 130, 'nouveau-sort')], '/mnt/files/shorts')
#   decouper_auto('/mnt/files/video.mp4', '/mnt/files/shorts', duree=45, maxi=6)   # tranches régulières
import os, shutil, subprocess

def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def duree_video(chemin):
    out = subprocess.run([_ffmpeg(), '-i', chemin], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration:')[1].split(',')[0].strip().split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

FILTRE = ('[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];'
          '[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]')

def decouper(video, segments, sortie, max_s=59):
    os.makedirs(sortie, exist_ok=True)
    fichiers = []
    for i, (debut, fin, nom) in enumerate(segments, 1):
        fin = min(fin, debut + max_s)
        dest = os.path.join(sortie, f'short{i:02d}_{nom}.mp4')
        cmd = [_ffmpeg(), '-y', '-ss', str(debut), '-i', video, '-t', str(fin - debut), '-filter_complex', FILTRE,
               '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
               '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', dest]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-500:])
        fichiers.append(dest)
    return fichiers

def decouper_auto(video, sortie, duree=45, maxi=6):
    total = duree_video(video)
    segs, t, i = [], 0.0, 1
    while t + 8 <= total and len(segs) < maxi:   # ignore les restes de moins de 8 s
        segs.append((round(t, 1), round(min(t + duree, total), 1), f'partie{i}'))
        t += duree; i += 1
    return decouper(video, segs, sortie)
