import os, asyncio
from helper.utils import metadata_text

async def change_metadata(input_file, output_file, metadata, filename="", site=""):
    author, title, video_title, audio_title, subtitle_title = await metadata_text(metadata, filename, site)

    cmd = [
        'ffmpeg',
        '-y',
        '-i', input_file,
        '-map_metadata', '-1',
        '-map', '0',
        '-c', 'copy'
    ]

    if title:
        cmd.extend(['-metadata', f'title={title}'])
    if author:
        cmd.extend(['-metadata', f'author={author}'])
        cmd.extend(['-metadata', f'artist={author}'])

    if video_title:
        cmd.extend(['-metadata:s:v', f'title={video_title}'])
    if audio_title:
        cmd.extend(['-metadata:s:a', f'title={audio_title}'])
    if subtitle_title:
        cmd.extend(['-metadata:s:s', f'title={subtitle_title}'])

    if output_file.lower().endswith('.mkv'):
        cmd.extend(['-f', 'matroska'])

    cmd.append(output_file)

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        if process.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True

        print(f"FFmpeg error (code {process.returncode}): {stderr.decode('utf-8', errors='ignore')}")

        fallback_cmd = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-map_metadata', '-1',
            '-map', '0:v?',
            '-map', '0:a?',
            '-c:v', 'copy',
            '-c:a', 'copy'
        ]

        if title:
            fallback_cmd.extend(['-metadata', f'title={title}'])
        if author:
            fallback_cmd.extend(['-metadata', f'author={author}'])
            fallback_cmd.extend(['-metadata', f'artist={author}'])
        if video_title:
            fallback_cmd.extend(['-metadata:s:v', f'title={video_title}'])
        if audio_title:
            fallback_cmd.extend(['-metadata:s:a', f'title={audio_title}'])

        if output_file.lower().endswith('.mkv'):
            fallback_cmd.extend(['-f', 'matroska'])

        fallback_cmd.append(output_file)

        fallback_process = await asyncio.create_subprocess_exec(
            *fallback_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, fallback_stderr = await fallback_process.communicate()

        if fallback_process.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        else:
            print(f"FFmpeg fallback error (code {fallback_process.returncode}): {fallback_stderr.decode('utf-8', errors='ignore')}")
            return False

    except Exception as e:
        print(f"Error in change_metadata: {e}")
        return False
