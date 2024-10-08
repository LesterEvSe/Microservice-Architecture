from tempdb import UserDB

if __name__ == "__main__":
    # Налаштування підключення до PostgreSQL
    db = UserDB(dbname="users", user="user_admin", password="eighty9@doublet", host="user-db", port="5432")

    # Додати користувачів
    user_id = db.add_user("test_user", "test_user@example.com")
    print(f"Користувач створений з ID: {user_id}")

    # Отримати список користувачів
    users = db.get_users()
    print("Список користувачів:")
    for user in users:
        print(user)
    db.close()
