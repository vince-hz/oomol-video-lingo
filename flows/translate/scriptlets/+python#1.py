from oocana import Context
import os, sys

vlPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "VideoLingo")

# switch to vlPath
os.chdir(vlPath)
sys.path.append(vlPath)

from batch.utils.video_processor import process_video, INPUT_DIR, SAVE_DIR
from core.config_utils import update_key, load_key

def workaroundInstallSudachiPy():
  try:
    import sudachipy
    print("sudachipy is installed")
  except ImportError:
    print("sudachipy is not installed")
    # install sudachipy from source in /tmp.
    os.system("git clone https://github.com/WorksApplications/SudachiPy.git /tmp/SudachiPy")
    os.chdir("/tmp/SudachiPy")
    os.system("pip install .")
    os.chdir(vlPath) # switch back to vlPath

def main(params: dict, context: Context):
  update_key("api.key", params["apikey"])
  update_key("api.base_url", "https://api.openai-hk.com")
  update_key("api.model", "gemini-pro")
  update_key("whisper.language", params["source_language"])

  if load_key("whisper.language") == "ja":
    workaroundInstallSudachiPy()

  videoPath = params["videoPath"]
  videoFullName = os.path.basename(videoPath)
  targetDir = os.path.join(vlPath, INPUT_DIR)
  os.makedirs(targetDir, exist_ok=True)
  os.system(f"cp {videoPath} {targetDir}")
  print(f"copy {videoPath} to {targetDir}")
  videoPath = os.path.join(targetDir, videoFullName)

  status, error_step, error_message = process_video(videoFullName, mergeSubtitles_to_video=params["mergeSubtitles_to_video"])
  status_msg = "Done" if status else f"Error: {error_step} - {error_message}"
  if not status:
    raise Exception(status_msg)

  videoName = os.path.splitext(videoFullName)[0]
  outputDir = os.path.join(vlPath, SAVE_DIR, videoName)
  subtitle_path = os.path.join(outputDir, "trans_src.srt")
  subtitle_str = open(subtitle_path, "r").read()
  context.preview({
    "type": "text",
    "data": subtitle_str
  })
  return { "subtitle_path": subtitle_path }
