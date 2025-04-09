from django.contrib import admin

# Register your models here.

async def check_client_exists(all_pending_friend, client_to_check):
    for pending_friend in all_pending_friend:
        print(pending_friend["client"])
        if pending_friend["client"] == client_to_check:
            print("already a client inside the pending list")
            return await pending_friend["username"]
    return None