
import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # bot client config
    API_ID = os.environ.get("API_ID", "")
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    BOT = None

    # STRING_SESSION is optional now - bot will work without it (2GB limit)
STRING_SESSION = os.environ.get("STRING_SESSION", "") or None

# If no string, run with Bot Token only
if not STRING_SESSION:
    print("No STRING_SESSION found - Running in Bot mode (2GB limit)")
else:
    print("STRING_SESSION found - Running in Premium mode (4GB)")
    
    # database config
    DB_NAME = os.environ.get("DB_NAME","Cluster0")     
    DB_URL = os.environ.get("DB_URL","")
 
    # other configs
    IMAGE_URL = [
        "https://i.ibb.co/rGPvzbxz/2ffce4886029.jpg",
        "https://i.ibb.co/Wvrb15XR/890a2b4ae625.jpg",
        "https://i.ibb.co/6RtW5fnr/c9336e79330d.jpg",
        "https://i.ibb.co/VYhWYwYt/2ead323a38a8.jpg",
        "https://i.ibb.co/8gjQJFv4/da6bee925908.jpg"
    ]
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6426143861').split()]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002367970315"))

    # free upload limit 
    FREE_UPLOAD_LIMIT = 6442450944 # calculation 6*1024*1024*1024=results

    # premium mode feature 
    UPLOAD_LIMIT_MODE = False 
    PREMIUM_MODE = False 
    
    #force subs
    try:
        FORCE_SUB = int(os.environ.get("FORCE_SUB", "")) 
    except:
        FORCE_SUB = os.environ.get("FORCE_SUB", "CodeRips")
        
    # wes response configuration     
    PORT = int(os.environ.get("PORT", "8080"))
    BOT_UPTIME = time.time()

class Txt(object):
    # part of text configuration
    START_TXT = """✨ <b>Hey, {}! Welcome</b> 👋

🚀 <b>I am an Advanced & High-Speed Telegram Rename Bot!</b>

⚡ <b><u>Key Features:</u></b>
• <b>Rename Files & Videos</b> with lightning speed.
• <b>Custom Thumbnail</b> & <b>Custom Caption</b> support.
• <b>Prefix & Suffix</b> customization for filenames.
• <b>Custom Metadata Editor</b> for videos and media files.
• <b>Convert Video to File</b> and <b>File to Video</b> seamlessly.

💎 <i>Created with ❤️ by:</i> <a href="https://t.me/CodeRips"><b>CodeRips</b></a>"""

    ABOUT_TXT = """<b>✨ <u>About This Bot</u></b>

<b>🤖 Bot Name :</b> {}
<b>🖥️ Developer :</b> {}
<b>👨‍💻 Programmer :</b> {}
<b>📕 Library :</b> {}
<b>✏️ Language :</b> {}
<b>💾 Database :</b> {}
<b>📊 Version :</b> <a href="https://t.me/Renox_Rename_Bot">{}</a>

💬 <b>Need Help?</b> Contact <a href="https://t.me/CodeRips">@CodeRips</a>"""

    HELP_TXT = """✨ <b><u>User Guide & Help Menu</u></b>

<b>1. How to Rename a File:</b>
• Send any document, video, or audio file.
• Enter the desired new file name.
• Choose output format (<b>Document</b>, <b>Video</b>, or <b>Audio</b>).

<b>2. Customization Commands:</b>
• <b>Thumbnail:</b> Send any photo to set it as a thumbnail.
• <b>Caption:</b> Use <code>/set_caption</code> to format custom captions.
• <b>Prefix/Suffix:</b> Use <code>/set_prefix</code> & <code>/set_suffix</code> to append text.
• <b>Metadata:</b> Use <code>/metadata</code> to toggle or set custom file metadata.

ℹ️ <b>Support Channel:</b> <a href="https://t.me/Code_Rips_Support">CodeRips Support</a>"""

    UPGRADE_PREMIUM = """💎 <b><u>Premium Subscription Plans</u></b>

★ <b>Bronze Plan:</b> 3 Days - ₹39
★ <b>Silver Plan:</b> 7 Days - ₹59
★ <b>Gold Plan:</b> 15 Days - ₹99
★ <b>Platinum Plan:</b> 1 Month - ₹179
★ <b>Diamond Plan:</b> 2 Months - ₹339

✨ <b><u>Benefits:</u></b>
• ⚡ <b>Unlimited Daily Uploads</b>
• 🚀 <b>Priority High-Speed Processing</b>
• 📂 <b>Supports Large Files (4GB+)</b>

<i>Discount of ₹9 applied on all plans!</i>
💳 <b>Contact Admin:</b> <a href="https://t.me/ZENCURSE">ZENCURSE</a>"""
    
    UPGRADE_PLAN = """💎 <b><u>Pro Upload Limit Plans</u></b>

🔹 <b>Plan: Pro</b>
• Duration: 1 Month | Limit: 100 GB | Price: ₹179

🔹 <b>Plan: Ultra Pro</b>
• Duration: 1 Month | Limit: 1000 GB | Price: ₹199

✨ <b>Discount on all plans: ₹9 OFF!</b>
💳 <b>Buy Now:</b> Contact <a href="https://t.me/ZENCURSE">ZENCURSE</a>"""
    
    THUMBNAIL = """🖼️ <b><u>Custom Thumbnail Settings</u></b>

<b>• Set Thumbnail:</b> Send any photo directly to save it as your custom thumbnail.
<b>• View Thumbnail:</b> Use /view_thumb to see your active thumbnail.
<b>• Delete Thumbnail:</b> Use /del_thumb to remove your thumbnail."""

    CAPTION = """📝 <b><u>Custom Caption Settings</u></b>

<b>• Set Caption:</b> <code>/set_caption {filename}</code>
<b>• View Caption:</b> /see_caption
<b>• Delete Caption:</b> /del_caption

<b><u>Available Dynamic Tags:</u></b>
• <code>{filename}</code> - Name of the output file
• <code>{filesize}</code> - Formatted size of the file
• <code>{duration}</code> - Video/Audio duration

<b>Example:</b>
<code>/set_caption 🎬 <b>File:</b> {filename}
💾 <b>Size:</b> {filesize}
⏰ <b>Duration:</b> {duration}</code>"""

    BOT_STATUS = """⚡ <b><u>Current Bot Statistics</u></b>

⏱️ <b>Uptime:</b> <code>{}</code>
👥 <b>Total Users:</b> <code>{}</code>
💎 <b>Premium Users:</b> <code>{}</code>
⬆️ <b>Uploaded:</b> <code>{}</code>
⬇️ <b>Downloaded:</b> <code>{}</code>"""

    LIVE_STATUS = """📊 <b><u>Live System Server Status</u></b>

⏱️ <b>Uptime:</b> <code>{}</code>
💻 <b>CPU Load:</b> <code>{}%</code>
🧠 <b>RAM Usage:</b> <code>{}%</code>
💾 <b>Disk Usage:</b> <code>{}%</code> (Used: <code>{}</code> / Total: <code>{}</code>)
📁 <b>Free Disk:</b> <code>{}</code>
📡 <b>Net IO:</b> ⬆️ <code>{}</code> | ⬇️ <code>{}</code>
⚡ <i>Engine: v3.0.0 Stable</i>"""

    DIGITAL_METADATA = """🏷️ <b><u>Custom Metadata Setup</u></b>

Use <code>/metadata [code]</code> or reply with your code.

<b>Sample Code Format:</b>
<code>--change-title @CodeRips
--change-video-title @CodeRips
--change-audio-title @CodeRips
--change-subtitle-title @CodeRips
--change-author @CodeRips</code>

📥 <b>Help & Support:</b> <a href="https://t.me/Code_Rips_Support">CodeRips Support</a>"""
    
    CUSTOM_FILE_NAME = """✒️ <b><u>Custom Prefix & Suffix Settings</u></b>

<b>Prefix (Added before filename):</b>
• <code>/set_prefix [Prefix]</code> - Set Prefix
• <code>/see_prefix</code> - View Prefix
• <code>/del_prefix</code> - Delete Prefix

<b>Suffix (Added after filename):</b>
• <code>/set_suffix [Suffix]</code> - Set Suffix
• <code>/see_suffix</code> - View Suffix
• <code>/del_suffix</code> - Delete Suffix

<b>Example:</b> <code>/set_prefix [HEVC]</code> or <code>/set_suffix @CodeRips</code>"""
    
    DEV_TXT = """✨ <b><u>Special Thanks & Credits</u></b>

» <b>Source Code:</b> <a href="https://graph.org/Nigga-09-13-4">Renox Rename Bot</a>

❣️ <b>Developers & Supporters:</b>
• <a href="https://t.me/CodeRips">CodeRips</a>
• <a href="https://t.me/ZENCURSE">ZENCURSE</a>"""

    SEND_METADATA = """🏷️ <b><u>Set Custom Metadata</u></b>

Reply to this message with your metadata code.

<b>Example:</b>
<code>--change-title @CodeRips
--change-video-title @CodeRips
--change-audio-title @CodeRips
--change-author @CodeRips</code>"""
    
    PROGRESS_BAR = """<b>
┌━━━━━━━━━━━━━━━━━━━━┐
├ 🚀 <b>Status:</b> {5}
├ 📦 <b>Size:</b> {1} / {2}
├ 📊 <b>Progress:</b> {0}%
├ ⚡ <b>Speed:</b> {3}/s
├ ⏰ <b>ETA:</b> {4}
└━━━━━━━━━━━━━━━━━━━━┘</b>"""
