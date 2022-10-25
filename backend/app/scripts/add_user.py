import asyncio
import os
import secrets

from backend.app.utils.security import get_password_hash
from backend.common.db.init import init_db
from backend.common.models.user import User


async def create_system_users():

    list = ["Admin", "Api", "Scheduler"]
    admin_exists = False
    scheduler_exists = False
    api_exists = False

    query = {
        "full_name": {"$in": list},
    }

    async for user in User.find_many(query):
        if user.full_name.lower() == "admin":
            admin_exists = True
        elif user.full_name.lower() == "api":
            api_exists = True
        elif user.full_name.lower() == "scheduler":
            scheduler_exists = True

    if not admin_exists:
        await create_admin_user(email="admin@mmitnetwork.com", full_name="Admin")

    if not api_exists:
        await create_admin_user(email="api@mmitnetwork.com", full_name="Api")

    if not scheduler_exists:
        await create_admin_user(email="scheduler@mmitnetwork.com", full_name="Scheduler")


async def create_admin_user(email="admin@mmitnetwork.com", full_name="Admin", plain_pass=None):
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
    print(f"Created {full_name} user with email: {email}, password: {plain_pass}")
    return user, plain_pass


async def execute():
    await init_db()
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(execute())
