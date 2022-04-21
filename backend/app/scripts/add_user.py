import asyncio
import os
import secrets

from backend.app.utils.security import get_password_hash
from backend.common.models.user import User
from backend.common.db.init import init_db


async def create_admin_user(
    email="admin@mmitnetwork.com", full_name="Admin", plain_pass=None
):
    if not plain_pass:
        if os.path.exists("/usr/share/dict/words"):
            with open("/usr/share/dict/words") as f:
                words = [word.strip() for word in f]
                plain_pass = "-".join(secrets.choice(words) for _ in range(4))
        else:
            plain_pass = secrets.token_hex(16)

    user = User(
        email=email,
        full_name=full_name,
        is_admin=True,
        hashed_password=get_password_hash(plain_pass),
    )
    await user.save()
    return user, plain_pass


async def execute():
    await init_db()
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(execute())
