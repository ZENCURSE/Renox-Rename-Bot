import pytest
import pytest_asyncio
import mongomock_motor
from helper.database import Database
from helper.utils import metadata_text

@pytest.fixture
def mock_db():
    db = Database("mongodb://localhost:27017", "test_db")
    db._client = mongomock_motor.AsyncMongoMockClient()
    db.db = db._client.get_database("test_db")
    db.col = db.db.get_collection("user")
    db.premium = db.db.get_collection("premium")
    return db

@pytest.mark.asyncio
async def test_database_metadata_and_site(mock_db):
    user_id = 123456789

    # Default values check
    mode = await mock_db.get_metadata(user_id)
    assert mode is False

    code = await mock_db.get_metadata_code(user_id)
    assert code == "By :- @Unrated_Coder"

    is_meta_custom = await mock_db.get_metadata_custom_status(user_id)
    assert is_meta_custom is False

    site = await mock_db.get_metadata_site(user_id)
    assert site == "https://www.anireal-anime.top/"

    is_site_custom = await mock_db.get_site_custom_status(user_id)
    assert is_site_custom is False

    class MockUser:
        def __init__(self, uid):
            self.id = uid
            self.mention = "User"
            self.username = "user"
    class MockBot:
        def __init__(self):
            self.mention = "Bot"
        async def send_message(self, *args, **kwargs):
            pass

    await mock_db.add_user(MockBot(), type("Msg", (), {"from_user": MockUser(user_id)})())

    # Set custom metadata code and enable mode
    await mock_db.set_metadata_code(user_id, "By :- @MyCustomChannel", is_custom=True)
    await mock_db.set_metadata(user_id, True)

    assert await mock_db.get_metadata(user_id) is True
    assert await mock_db.get_metadata_code(user_id) == "By :- @MyCustomChannel"
    assert await mock_db.get_metadata_custom_status(user_id) is True

    # Set custom site
    await mock_db.set_metadata_site(user_id, "https://mycustomsite.com", is_custom=True)
    assert await mock_db.get_metadata_site(user_id) == "https://mycustomsite.com"
    assert await mock_db.get_site_custom_status(user_id) is True

@pytest.mark.asyncio
async def test_metadata_text_parsing():
    raw_code = "--change-title {filename}\n--change-author @Unrated_Coder\n--change-video-title {site}"
    filename = "Sample.mp4"
    site = "https://mysite.org"

    author, title, video_title, audio_title, subtitle_title = await metadata_text(raw_code, filename=filename, site=site)

    assert title == "Sample.mp4"
    assert author == "@Unrated_Coder"
    assert video_title == "https://mysite.org"
    assert audio_title is None
    assert subtitle_title is None

@pytest.mark.asyncio
async def test_metadata_text_fallback():
    raw_code = "By :- @Unrated_Coder"
    author, title, video_title, audio_title, subtitle_title = await metadata_text(raw_code)

    assert author == "By :- @Unrated_Coder"
    assert title == "By :- @Unrated_Coder"
    assert video_title == "By :- @Unrated_Coder"

@pytest.mark.asyncio
async def test_progress_status_text():
    from helper.utils import progress_for_pyrogram
    import time
    class MockMsg:
        def __init__(self):
            self.text = ""
        async def edit(self, text, reply_markup=None):
            self.text = text

    msg = MockMsg()
    start = time.time() - 5
    await progress_for_pyrogram(50, 100, "MyMovie.mkv", msg, start, op_type="download")
    assert "Downloading..." in msg.text
    assert "MyMovie.mkv" in msg.text

    await progress_for_pyrogram(50, 100, "MyMovie.mkv", msg, start, op_type="upload")
    assert "Uploading..." in msg.text
    assert "MyMovie.mkv" in msg.text

@pytest.mark.asyncio
async def test_remove_path_directory_handling(tmp_path):
    from helper.utils import remove_path
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()

    # remove_path should safely ignore directories without throwing IsADirectoryError
    await remove_path(str(dir_path))
    assert dir_path.exists()
