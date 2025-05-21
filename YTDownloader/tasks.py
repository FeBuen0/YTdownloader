from celery_worker import celery
from yt_dlp import YoutubeDL
import subprocess
import os

DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@celery.task(bind=True, name='tasks.download_and_merge')
def download_and_merge(self, url):
    video_path = os.path.join(DOWNLOAD_FOLDER, f"{self.request.id}_video.mp4")
    audio_path = os.path.join(DOWNLOAD_FOLDER, f"{self.request.id}_audio.webm")
    final_path = os.path.join(DOWNLOAD_FOLDER, f"{self.request.id}_final.mp4")

    self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Baixando vídeo'})
    with YoutubeDL({'format': 'bestvideo', 'outtmpl': video_path, 'quiet': True}) as ydl:
        ydl.download([url])

    self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Baixando áudio'})
    with YoutubeDL({'format': 'bestaudio', 'outtmpl': audio_path, 'quiet': True}) as ydl:
        ydl.download([url])

    self.update_state(state='PROGRESS', meta={'progress': 75, 'status': 'Unindo vídeo e áudio'})
    subprocess.run([
        'ffmpeg', '-i', video_path, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
        final_path, '-y'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(video_path)
    os.remove(audio_path)

    self.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Finalizado'})
    return {'download_link': f'/static/downloads/{self.request.id}_final.mp4'}
