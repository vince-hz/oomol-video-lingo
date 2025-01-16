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
  # 判断 llm 是否是 object.
  if params["llm"] is None or params["llm"] == "":
    update_key("api.key", context.oomol_llm_env.get('api_key'))
    update_key("api.base_url", context.oomol_llm_env.get('base_url'))
    update_key("api.model", context.oomol_llm_env.get('models')[0])
  else:
    update_key("api.key", params["llm"]["api-key"])
    update_key("api.base_url", params["llm"]["base-url"])
    update_key("api.model", params["llm"]["model"])

  update_key("whisper.language", params["source-language"])

  if load_key("whisper.language") == "ja":
    workaroundInstallSudachiPy()

  videoPath = params["video-path"]
  mergeSubtitle = params["merge-subtitles-to-video"]

  input_file = ""
  if videoPath.startswith("http"):
    input_file = videoPath
  else:
    # copy file to target dir.
    videoFullName = os.path.basename(videoPath)
    targetDir = os.path.join(vlPath, INPUT_DIR)
    os.makedirs(targetDir, exist_ok=True)
    os.system(f"cp {videoPath} {targetDir}")
    print(f"copy {videoPath} to {targetDir}")
    videoPath = os.path.join(targetDir, videoFullName)
    input_file = videoFullName

  status, error_step, error_message, processed_videoName = process_video(input_file, mergeSubtitles_to_video=mergeSubtitle)
  status_msg = "Done" if status else f"Error: {error_step} - {error_message}"
  if not status:
    raise Exception(status_msg)

  outputDir = os.path.join(vlPath, SAVE_DIR, processed_videoName)
  subtitle_path = os.path.join(outputDir, "trans_src.srt")
  subtitle_str = open(subtitle_path, "r").read()
  
  context.preview({
    "type": "text",
    "data": subtitle_str
  })
  return { "subtitle-path": subtitle_path }
