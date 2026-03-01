#!/usr/bin/env python3
"""Helper script to promote a user to admin role."""

import sys
from app.database import get_db

def make_admin(email: str):
    """Promote a user to admin by email."""
    db = get_db()

    # Check if user exists
    result = db.table("users").select("id, email, role").eq("email", email).execute()

    if not result.data:
        print(f"❌ User with email '{email}' not found")
        return False

    user = result.data[0]
    print(f"Found user: {user['email']} (current role: {user.get('role', 'user')})")

    # Update to admin
    db.table("users").update({"role": "admin"}).eq("id", user["id"]).execute()
    print(f"✅ User '{email}' is now an admin!")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db/make_admin.py <email>")
        print("Example: python db/make_admin.py admin@example.com")
        sys.exit(1)

    email = sys.argv[1]
    make_admin(email)
