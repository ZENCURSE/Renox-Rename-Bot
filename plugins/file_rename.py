import os
import re
import time
import asyncio
from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import unrated_coder
from helper.ffmpeg import change_metadata
from config import Config

UPLOAD_TEXT = """Uploading Started...."""
DOWNLOAD_TEXT = """Download Started..."""

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)


@Client.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def rename_start(client, message):
    user_id = message.from_user.id
    media_file = getattr(message, message.media.value)
    filename = getattr(media_file, "file_name", "Unknown")
    filesize = humanbytes(media_file.file_size)
    mime_type = getattr(media_file, "mime_type", "application/octet-stream")
    dcid = FileId.decode(media_file.file_id).dc_id
    extension_type = mime_type.split('/')[0] if mime_type else "FILE"

    if client.premium and client.uploadlimit:
        await unrated_coder.reset_uploadlimit_access(user_id)
        user_data = await unrated_coder.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit) - int(used)
        used_percentage = int(used) / int(limit) * 100 if int(limit) > 0 else 0
        if remain < int(media_file.file_size):
            return await message.reply_text(
                f"{used_percentage:.2f}% Of Daily Upload Limit {humanbytes(limit)}.\n\n"
                f" Media Size: {filesize}\n Your Used Daily Limit {humanbytes(used)}\n\n"
                f"You have only **{humanbytes(remain)}** Data.\nPlease, Buy Premium Plans.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 Uᴘɢʀᴀᴅᴇ", callback_data="plans")]])
            )

    if await unrated_coder.has_premium_access(user_id) and client.premium:
        if not Config.STRING_SESSION:
            if media_file.file_size > 2000 * 1024 * 1024:
                return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ+")

        prompt_text = (
            f"**__MEDIA INFO__**\n\n"
            f"◈ **Old File Name:** `{filename}`\n"
            f"◈ **Extension:** `{extension_type.upper()}`\n"
            f"◈ **File Size:** `{filesize}`\n"
            f"◈ **MIME Type:** `{mime_type}`\n"
            f"◈ **DC ID:** `{dcid}`\n\n"
            f"👉 **Please enter the new filename with extension and reply to this message....**"
        )
        try:
            await message.reply_text(
                text=prompt_text,
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True)
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_text(
                text=prompt_text,
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True)
            )
        except Exception as e:
            print(f"Error in rename_start: {e}")
    else:
        if media_file.file_size > 2000 * 1024 * 1024 and client.premium:
            return await message.reply_text("If you want to rename 4GB+ files then you will have to buy premium. /plans")

        prompt_text = (
            f"**__MEDIA INFO__**\n\n"
            f"◈ **Old File Name:** `{filename}`\n"
            f"◈ **Extension:** `{extension_type.upper()}`\n"
            f"◈ **File Size:** `{filesize}`\n"
            f"◈ **MIME Type:** `{mime_type}`\n"
            f"◈ **DC ID:** `{dcid}`\n\n"
            f"👉 **Please enter the new filename with extension and reply to this message....**"
        )
        try:
            await message.reply_text(
                text=prompt_text,
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True)
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_text(
                text=prompt_text,
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True)
            )
        except Exception as e:
            print(f"Error in rename_start (non-premium): {e}")


@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message

    # Verify karein ki reply message exist karta hai aur wo bot ka hi prompt message hai
    if not reply_message or not reply_message.from_user or not reply_message.from_user.is_self:
        await message.continue_propagation()
        return

    reply_text = reply_message.text or ""
    reply_text_lower = reply_text.lower()
    valid_keywords = ["media info", "enter the new filename", "file name"]

    # Agar prompt me rename se related text nahi hai to ignore karein
    if not any(k in reply_text_lower for k in valid_keywords):
        await message.continue_propagation()
        return

    new_name = message.text
    if not new_name:
        return await message.reply("⚠️ **Please send a valid file name.**")

    # Original file message ko direct fetch karein
    file_id = reply_message.reply_to_message_id
    if not file_id:
        return await message.reply("⚠️ **Original file reference not found!**")

    try:
        file = await client.get_messages(message.chat.id, file_id)
    except Exception:
        file = None

    if not file or not getattr(file, "media", None):
        return await message.reply("⚠️ **Original file message not found or expired!**")

    media = getattr(file, file.media.value)

    # Extension manage karein agar user ne extension nahi diya
    if "." not in new_name:
        orig_filename = getattr(media, "file_name", "")
        if orig_filename and "." in orig_filename:
            extn = orig_filename.rsplit('.', 1)[-1]
        else:
            extn = "mkv"
        new_name = f"{new_name}.{extn}"

    # Chat ko clean karne ke liye messages delete karein
    try:
        await message.delete()
        await reply_message.delete()
    except Exception:
        pass

    button = [[InlineKeyboardButton("📁 Dᴏᴄᴜᴍᴇɴᴛ", callback_data="upload#document")]]
    if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
        button.append([InlineKeyboardButton("🎥 Vɪᴅᴇᴏ", callback_data="upload#video")])
    elif file.media == MessageMediaType.AUDIO:
        button.append([InlineKeyboardButton("🎵 Aᴜᴅɪᴏ", callback_data="upload#audio")])

    await client.send_message(
        chat_id=message.chat.id,
        text=f"**Sᴇʟᴇᴄᴛ Tʜᴇ Oᴜᴛᴩᴜᴛ Fɪʟᴇ Tyᴩᴇ**\n**• Fɪʟᴇ Nᴀᴍᴇ :-** `{new_name}`",
        reply_to_message_id=file.id,
        reply_markup=InlineKeyboardMarkup(button)
    )


async def upload_files(bot, sender_id, upload_type, file_path, ph_path, caption, duration, processing_status, filename=""):
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"

        status_ud = filename if filename else UPLOAD_TEXT

        if upload_type == "document":
            filw = await bot.send_document(
                sender_id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=(status_ud, processing_status, time.time(), "upload")
            )
        elif upload_type == "video":
            filw = await bot.send_video(
                sender_id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(status_ud, processing_status, time.time(), "upload")
            )
        elif upload_type == "audio":
            filw = await bot.send_audio(
                sender_id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(status_ud, processing_status, time.time(), "upload")
            )
        else:
            return None, f"Unknown upload type: {upload_type}"

        return filw, None
    except Exception as e:
        return None, str(e)


async def safe_edit_status(msg, text):
    try:
        return await msg.edit(text)
    except Exception as e:
        print(f"Error editing status message: {e}")
        return msg

async def upload_doc(bot, update):
    user_id = int(update.message.chat.id)
    raw_text = update.message.text or ""
    
    match = re.search(r":-\s*`?([^`\n]+)`?", raw_text)
    if match:
        new_filename_ = match.group(1).strip(" `*\n\r")
    elif ":-" in raw_text:
        new_filename_ = raw_text.split(":-", 1)[1].strip(" `*\n\r")
    else:
        new_filename_ = raw_text.strip(" `*\n\r")

    processing_status = await safe_edit_status(update.message, "`Processing...`")

    os.makedirs("Metadata", exist_ok=True)
    os.makedirs("Renames", exist_ok=True)
    user_data = await unrated_coder.get_user_data(user_id)

    try:
        prefix = user_data.get('prefix', None)
        suffix = user_data.get('suffix', None)
        new_filename = await add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await safe_edit_status(processing_status, f"⚠️ Something went wrong can't able to set Prefix or Suffix ☹️ \nError: {e}")

    # Callback update me reply_to_message check aur fallback fetching
    file = update.message.reply_to_message
    if not file and update.message.reply_to_message_id:
        try:
            file = await bot.get_messages(update.message.chat.id, update.message.reply_to_message_id)
        except Exception:
            file = None

    if not file or not getattr(file, "media", None):
        return await safe_edit_status(processing_status, "⚠️ **Original file message not found or expired!**")

    media = getattr(file, file.media.value)

    file_path = f"Renames/{new_filename}"
    metadata_path = f"Metadata/{new_filename}"

    await safe_edit_status(processing_status, "`Try To Download....`")
    if bot.premium and bot.uploadlimit:
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        total_used = int(used) + int(media.file_size)
        await unrated_coder.set_used_limit(user_id, total_used)

    try:
        dl_path = await bot.download_media(
            message=file,
            file_name=file_path,
            progress=progress_for_pyrogram,
            progress_args=(new_filename, processing_status, time.time(), "download")
        )
    except Exception as e:
        if bot.premium and bot.uploadlimit:
            used_remove = int(used) - int(media.file_size)
            await unrated_coder.set_used_limit(user_id, used_remove)
        return await processing_status.edit(f"Download Error: {e}")

    metadata_mode = await unrated_coder.get_metadata_mode(user_id)
    if metadata_mode:
        metadata = await unrated_coder.get_metadata_code(user_id)
        site = await unrated_coder.get_metadata_site(user_id)
        if metadata:
            await safe_edit_status(processing_status, "I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")
            if await change_metadata(dl_path, metadata_path, metadata, new_filename, site=site):
                await safe_edit_status(processing_status, "Metadata Added.....")
            else:
                await safe_edit_status(processing_status, "Failed to add metadata, uploading original file...")
                metadata_mode = False
        else:
            await safe_edit_status(processing_status, "No metadata found, uploading original file...")
            metadata_mode = False
    else:
        await safe_edit_status(processing_status, "`Try To Uploading....`")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata and metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if parser:
            parser.close()
    except Exception as e:
        print(f"Error extracting metadata: {e}")

    ph_path = None
    c_caption = user_data.get('caption', None)
    c_thumb = user_data.get('file_id', None)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
        except Exception as e:
            if bot.premium and bot.uploadlimit:
                used_remove = int(used) - int(media.file_size)
                await unrated_coder.set_used_limit(user_id, used_remove)
            return await processing_status.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if c_thumb:
        try:
            ph_path = await bot.download_media(c_thumb)
            if ph_path and os.path.exists(ph_path):
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img.resize((320, 320))
                img.save(ph_path, "JPEG")
        except Exception as e:
            print(f"Error processing custom thumbnail: {e}")
            ph_path = None
    else:
        # Auto extract thumbnail frame from video if available
        src_file_for_thumb = dl_path if os.path.exists(dl_path) else file_path
        if src_file_for_thumb and os.path.exists(src_file_for_thumb):
            try:
                thumb_out = f"{src_file_for_thumb}_thumb.jpg"
                thumb_cmd = [
                    'ffmpeg', '-y',
                    '-ss', '00:00:02',
                    '-i', src_file_for_thumb,
                    '-vframes', '1',
                    '-q:v', '2',
                    thumb_out
                ]
                proc = await asyncio.create_subprocess_exec(
                    *thumb_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                if proc.returncode == 0 and os.path.exists(thumb_out) and os.path.getsize(thumb_out) > 0:
                    ph_path = thumb_out
                    img = Image.open(ph_path).convert("RGB")
                    img.resize((320, 320))
                    img.save(ph_path, "JPEG")
            except Exception as e:
                print(f"Error auto-generating video thumbnail: {e}")
                ph_path = None

        if not ph_path and getattr(media, "thumbs", None):
            try:
                ph_path = await bot.download_media(media.thumbs[0].file_id)
                if ph_path and os.path.exists(ph_path):
                    Image.open(ph_path).convert("RGB").save(ph_path)
                    img = Image.open(ph_path)
                    img.resize((320, 320))
                    img.save(ph_path, "JPEG")
            except Exception as e:
                print(f"Error processing media thumbnail: {e}")
                ph_path = None

    upload_type = update.data.split("#")[1]
    final_file_path = metadata_path if metadata_mode and os.path.exists(metadata_path) else file_path

    if media.file_size > 2000 * 1024 * 1024:
        filw, error = await upload_files(
            app, Config.LOG_CHANNEL, upload_type, final_file_path,
            ph_path, caption, duration, processing_status, filename=new_filename
        )

        if error:
            if bot.premium and bot.uploadlimit:
                used_remove = int(used) - int(media.file_size)
                await unrated_coder.set_used_limit(user_id, used_remove)
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await processing_status.edit(f"Upload Error: {error}")

        from_chat = filw.chat.id
        mg_id = filw.id
        await asyncio.sleep(2)
        await bot.copy_message(update.from_user.id, from_chat, mg_id)
        await bot.delete_messages(from_chat, mg_id)
    else:
        filw, error = await upload_files(
            bot, update.message.chat.id, upload_type, final_file_path,
            ph_path, caption, duration, processing_status, filename=new_filename
        )

        if error:
            if bot.premium and bot.uploadlimit:
                used_remove = int(used) - int(media.file_size)
                await unrated_coder.set_used_limit(user_id, used_remove)
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await processing_status.edit(f"Upload Error: {error}")

    await remove_path(ph_path, file_path, dl_path, metadata_path)
    return await safe_edit_status(processing_status, "Uploaded Successfully....")
