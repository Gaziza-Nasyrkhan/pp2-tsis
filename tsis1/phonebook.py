import psycopg2
import csv
import json

conn = psycopg2.connect(
    host = "localhost",
    database = "phonebooktsis",
    user = "postgres",
    password = "pp2psql"
    )

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS contacts CASCADE;")
cur.execute("DROP TABLE IF EXISTS groups;")
cur.execute("DROP TABLE IF EXISTS phones;")

conn.commit()
cur.execute("CREATE TABLE groups(id SERIAL PRIMARY KEY,name VARCHAR(50) UNIQUE NOT NULL);")
cur.execute("""CREATE TABLE contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            phone VARCHAR(100), 
            email VARCHAR(100),
            birthday DATE,
            group_id INTEGER REFERENCES groups(id));
            """)
cur.execute("CREATE TABLE phones(id SERIAL PRIMARY KEY,contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,phone VARCHAR(20) NOT NULL,type VARCHAR(10) CHECK(type IN ('home', 'work', 'mobile')));")
cur.execute("INSERT INTO groups(name) VALUES ('family'),('work'),('friend'),('other');")

conn.commit()

def choose_group():
    cur.execute("SELECT id, name FROM groups")
    groups = cur.fetchall()
    print("\ngroups:")
    for g in groups:
        print(f"  {g[0]}. {g[1]}")
    choice = input("Choose number groups: ").strip()
    return int(choice) if choice else None

def insert_from_csv():
    with open("contacts.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row)
            name  = row.get("name", "").strip()
            phone = row.get("phone", "").strip()
            email = row.get("email", "").strip() or None
            birthday = row.get("birthday", "").strip() or None
            group_name = row.get("group_name", "").strip() or None    

            group_id = None
            if group_name:
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                res = cur.fetchone()
                if res:
                    group_id = res[0]
            cur.execute(
    "INSERT INTO contacts (name, email, birthday, group_id)",
    (name, email, birthday, group_id)
)
            phone_type = row.get("phone_type", "").strip() or "mobile"

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            contact_id = cur.fetchone()[0]

            cur.execute(
    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
    (contact_id, phone, phone_type)
)
        conn.commit()
        print("Added successfully from CSV file!")


def insert_from_console():
    name = input("Enter the name: ").strip()
    phone = input("Enter the phone: ").strip()
    email = input("Enter the email: ").strip() or None
    birthday = input("Enter your birthday like(YYYY-MM-DD): ").strip() or None
    group_id = choose_group()

    cur.execute("INSERT INTO contacts (name, phone, email, birthday, group_id) VALUES (%s, %s, %s, %s, %s)", (name, phone, email, birthday, group_id))
    conn.commit()
    print(f"{name} added successfully!")


def update_con():
    name = input("Enter the name for updating data: ")
    print("What do you want to change?")
    print("1.Name")
    print("2.Phone")
    print("3.Email")
    print("4.Birthday")
    print("5.Group")

    choice = input("Enter your choice: ")
    if choice == "1":
        new_name = input("Enter a new name: ").strip()
        cur.execute("UPDATE contacts SET name = %s WHERE name = %s", (new_name, name))
    elif choice == "2":
        new_phone = input("Enter a new phone: ").strip()
        cur.execute("UPDATE contacts SET phone = %s WHERE name = %s", (new_phone, name))
    elif choice == "3":
        new_email = input("Enter a new email:").strip()
        cur.execute("UPDATE contacts SET email = %s WHERE name = %s", (new_email, name))
    elif choice == "4":
        new_birthday = input("Enter a new birthday:").strip()
        cur.execute("UPDATE contacts SET birthday = %s WHERE name = %s", (new_birthday, name))
    elif choice == "5":
        group_id = choose_group()
        cur.execute("UPDATE contacts SET group_id = %s WHERE name = %s", (group_id, name))

    else:
        print("Wrong choice!")
        return
    
    conn.commit()
    print("Updated succesfully!")

def delete_contacts():
    print("How do you want to delete?")
    print("1. With name")
    print("2. With phone")
    print("3. With email")


    choice = input("Enter your choice: ")
    if choice == "1":
        name1 = input("Enter the name: ")
        cur.execute("DELETE FROM contacts WHERE name = %s", (name1,))
    elif choice == "2":
        phone = input("Enter the phone: ")
        cur.execute("DELETE FROM contacts WHERE phone = %s", (phone,))
    elif choice == "3":
        email = input("Enter the email:")
        cur.execute("DELETE FROM contacts WHERE email = %s", (email,))
    else:
        print("Wrong choice!")
    conn.commit()

def search_contacts():
    query = input("Enter search: ")

    cur.execute("""
        SELECT c.id, c.name, c.phone, c.email, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.name ILIKE %s
           OR c.email ILIKE %s
           OR p.phone ILIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    rows = cur.fetchall()
    print_rows(rows)
  
def print_rows(rows):
    if not rows:
        print("empty")
        return
    print(f"\n{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25} {'Birthday':<12} {'Group':<10}")
    print("-"*90)
    for row in rows:
        print(f"{row[0]:<5} {str(row[1]):<20} {str(row[2]):<15} {str(row[3] or ''):<25} {str(row[4] or ''):<12} {str(row[5] or ''):<10}")


def filter_by_group():
    cur.execute("SELECT id, name FROM groups")
    groups = cur.fetchall()

    print("\ngroups:")
    for g in groups:
        print(f"  {g[0]}. {g[1]}")
    choice = input("Enter your choice: ").strip()
    if not choice.isdigit():
        print("Wrong choice!")
        return
 
    cur.execute("""
        SELECT c.id, c.name, c.phone, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.group_id = %s
        ORDER BY c.name
    """, (int(choice),))
    rows = cur.fetchall()
    if not rows:
        print("empty")
    else:
        print(f"\n{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25} {'Birthday':<12} {'Group':<10}")
        print("-"*90)
        for row in rows:
            print(f"{row[0]:<5} {str(row[1]):<20} {str(row[2]):<15} {str(row[3] or ''):<25} {str(row[4] or ''):<12} {str(row[5] or ''):<10}")


def sort_out():
    print("Sort by: \n1.name.\n2.birtday.\n3.id")
    choice = input("Your choice: ").strip()
    order = {"1": "c.name", "2": "c.birthday", "3": "c.id"}.get(choice)
    if not order:
        print("Қате таңдау!")
        return
 
    cur.execute(f"""
        SELECT c.id, c.name, c.phone, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order}
    """)
    rows = cur.fetchall()
    print_rows(rows)

def paginate():
    page = 0
    limit = 3
 
    while True:
        offset = page * limit
        cur.execute("""
            SELECT c.id, c.name, c.phone, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            ORDER BY c.id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()
 
        if not rows and page == 0:
            print("No contacts.")
            return
 
        print(f"\n─── Бет {page + 1} ───")
        print_rows(rows)
 
        if len(rows) < limit:
            print("(Last page)")
            cmd = input("prev / quit: ").strip().lower()
        else:
            cmd = input("next / prev / quit: ").strip().lower()
 
        if cmd == "next":
            if len(rows) == limit:
                page += 1
            else:
                print("no more page.")
        elif cmd == "prev":
            if page > 0:
                page -= 1
            else:
                print("without first page!")
        elif cmd == "quit":
            break


def export_to_json():
    cur.execute("""
        SELECT c.name, c.phone, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)
    rows = cur.fetchall()
    
    contacts = []
    for row in rows:
        contacts.append({
            "name": row[0],
            "phone": row[1],
            "email": row[2],
            "birthday": str(row[3]) if row[3] else None,
            "group": row[4]
        })
    
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)
    
    print("Exported successfully!")

def import_from_json():
    with open("contacts.json", "r") as f:
        contacts = json.load(f)
    
    for c in contacts:
        # group_id тап
        group_id = None
        if c.get("group"):
            cur.execute("SELECT id FROM groups WHERE name = %s", (c["group"],))
            res = cur.fetchone()
            if res:
                group_id = res[0]

        # аттас бар ма тексер
        cur.execute("SELECT id FROM contacts WHERE name = %s", (c["name"],))
        exists = cur.fetchone()
        
        if exists:
            choice = input(f"{c['name']} already exists. Skip or overwrite? (s/o): ").strip()
            if choice == "o":
                cur.execute("""
                    UPDATE contacts SET phone=%s, email=%s, birthday=%s, group_id=%s
                    WHERE name=%s
                """, (c["phone"], c["email"], c["birthday"], group_id, c["name"]))
            else:
                continue
        else:
            cur.execute("""
                INSERT INTO contacts (name, phone, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (c["name"], c["phone"], c["email"], c["birthday"], group_id))
    
    conn.commit()
    print("Imported successfully!")

try:
    while True:
        print("\n1.Insert data from a CSV file. \n2.Insert data from a console. \n3.Updating a contact's first name or phone number. \n4.Querying contacts with different filters (e.g. by name, by phone prefix). \n5.Deleting a contact by username or phone number\n6.Filter by group.\n7.Search by email.\n8.Sort the output by: name, birthday, or date added.\n9.Paginated navigation - navigate pages with next / prev / quit.\n10.Export to Json.\n11.Import from Json.")

        choice = input("Enter your choice: ")
        if choice == "1":
            insert_from_csv()
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_con()
        elif choice == "4":
            search_contacts()
        elif choice == "5":
            delete_contacts()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            search_contacts()
        elif choice == "8":
            sort_out()
        elif choice == "9":
            paginate()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        else:
            print("Wrong choice!")

        cur.execute("SELECT * FROM contacts;")
        print(cur.fetchall())
finally:
    cur.close()
    conn.close()
    print("Connection closed.")