import psycopg2
import csv
import json

# Database configuration - CHANGE THESE VALUES IF NEEDED
DB_NAME = "snake"
DB_USER = "postgres"
DB_PASSWORD = "pp2psql"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

def get_connection():
    """Create and return database connection"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check if database 'snake' exists")
        print("   3. Verify username and password")
        print("   4. Run: psql -U postgres -c 'CREATE DATABASE snake;'")
        raise

# Initialize connection
conn = get_connection()
cur = conn.cursor()

# Drop tables in correct order
cur.execute("DROP TABLE IF EXISTS phones CASCADE;")
cur.execute("DROP TABLE IF EXISTS contacts CASCADE;")
cur.execute("DROP TABLE IF EXISTS groups CASCADE;")
conn.commit()

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(100),
        birthday DATE,
        group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS phones (
        id SERIAL PRIMARY KEY,
        contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
        phone VARCHAR(20) NOT NULL,
        type VARCHAR(10) CHECK(type IN ('home', 'work', 'mobile'))
    )
""")

# Insert initial groups
cur.execute("""
    INSERT INTO groups(name) VALUES ('family'), ('work'), ('friend'), ('other') 
    ON CONFLICT (name) DO NOTHING
""")
conn.commit()

print("✅ Database setup completed!")

def choose_group():
    """Select a group from existing groups"""
    cur.execute("SELECT id, name FROM groups")
    groups = cur.fetchall()
    if not groups:
        return None
    print("\n📌 Available groups:")
    for g in groups:
        print(f"  {g[0]}. {g[1]}")
    try:
        choice = int(input("Choose group number: ").strip())
        for g in groups:
            if g[0] == choice:
                return choice
        return None
    except ValueError:
        return None

def insert_from_csv():
    """Import contacts from CSV file"""
    try:
        with open("contacts.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            print("\n📥 Importing contacts from CSV...")
            for row in reader:
                name = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                email = row.get("email", "").strip() or None
                birthday = row.get("birthday", "").strip() or None
                group_name = row.get("group_name", "").strip() or None
                phone_type = row.get("phone_type", "").strip() or "mobile"
                
                if not name or not phone:
                    print(f"⚠️  Warning: Missing name or phone for entry, skipped")
                    continue
                
                # Find group ID
                group_id = None
                if group_name:
                    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                    res = cur.fetchone()
                    if res:
                        group_id = res[0]
                
                # Insert contact
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id) 
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, birthday, group_id))
                contact_id = cur.fetchone()[0]
                
                # Insert phone
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type) 
                    VALUES (%s, %s, %s)
                """, (contact_id, phone, phone_type))
                
                count += 1
                print(f"  ✓ Added: {name} | Phone: {phone} | Group: {group_name or 'None'}")
            
            conn.commit()
            print(f"\n✅ Successfully imported {count} contacts from CSV!")
            show_all_contacts()
            
    except FileNotFoundError:
        print("❌ Error: contacts.csv file not found!")
        print("💡 Make sure 'contacts.csv' is in the same directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

def insert_from_console():
    """Insert contact manually from console"""
    print("\n📝 ADD NEW CONTACT")
    print("-" * 30)
    
    name = input("Full name: ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    phone = input("Phone number: ").strip()
    if not phone:
        print("❌ Phone number is required!")
        return
    
    email = input("Email (optional): ").strip() or None
    birthday = input("Birthday (YYYY-MM-DD, optional): ").strip() or None
    group_id = choose_group()
    
    # Phone type
    print("\nPhone type:")
    print("1. mobile")
    print("2. work")
    print("3. home")
    phone_type_choice = input("Choose phone type (1-3): ").strip()
    phone_type_map = {"1": "mobile", "2": "work", "3": "home"}
    phone_type = phone_type_map.get(phone_type_choice, "mobile")
    
    try:
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (name, email, birthday, group_id))
        contact_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO phones (contact_id, phone, type) 
            VALUES (%s, %s, %s)
        """, (contact_id, phone, phone_type))
        
        conn.commit()
        print(f"\n✅ {name} successfully added!")
        show_all_contacts()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

def update_contact():
    """Update contact information"""
    show_all_contacts()
    
    name = input("\nEnter the name of contact to update: ").strip()
    
    # Check if contact exists
    cur.execute("SELECT id, name FROM contacts WHERE name ILIKE %s", (f"%{name}%",))
    contacts = cur.fetchall()
    
    if not contacts:
        print("❌ Contact not found!")
        return
    
    if len(contacts) > 1:
        print("\n📋 Multiple contacts found:")
        for idx, (cid, cname) in enumerate(contacts, 1):
            print(f"  {idx}. {cname}")
        choice = int(input("Choose contact number: ")) - 1
        contact_id = contacts[choice][0]
        contact_name = contacts[choice][1]
    else:
        contact_id = contacts[0][0]
        contact_name = contacts[0][1]
    
    print(f"\n✏️  Updating: {contact_name}")
    print("\nWhat would you like to update?")
    print("1. Name")
    print("2. Phone")
    print("3. Email")
    print("4. Birthday")
    print("5. Group")
    print("6. Phone type")
    
    choice = input("\nYour choice (1-6): ").strip()
    
    try:
        if choice == "1":
            new_name = input("New name: ").strip()
            cur.execute("UPDATE contacts SET name = %s WHERE id = %s", (new_name, contact_id))
            print("✅ Name updated!")
            
        elif choice == "2":
            new_phone = input("New phone number: ").strip()
            cur.execute("UPDATE phones SET phone = %s WHERE contact_id = %s", (new_phone, contact_id))
            print("✅ Phone number updated!")
            
        elif choice == "3":
            new_email = input("New email: ").strip() or None
            cur.execute("UPDATE contacts SET email = %s WHERE id = %s", (new_email, contact_id))
            print("✅ Email updated!")
            
        elif choice == "4":
            new_birthday = input("New birthday (YYYY-MM-DD): ").strip() or None
            cur.execute("UPDATE contacts SET birthday = %s WHERE id = %s", (new_birthday, contact_id))
            print("✅ Birthday updated!")
            
        elif choice == "5":
            group_id = choose_group()
            cur.execute("UPDATE contacts SET group_id = %s WHERE id = %s", (group_id, contact_id))
            print("✅ Group updated!")
            
        elif choice == "6":
            print("\nPhone type:")
            print("1. mobile")
            print("2. work")
            print("3. home")
            type_choice = input("Choose new phone type (1-3): ").strip()
            type_map = {"1": "mobile", "2": "work", "3": "home"}
            new_type = type_map.get(type_choice, "mobile")
            cur.execute("UPDATE phones SET type = %s WHERE contact_id = %s", (new_type, contact_id))
            print("✅ Phone type updated!")
            
        else:
            print("❌ Invalid choice!")
            return
        
        conn.commit()
        print("\n✅ Contact updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

def search_contacts():
    """Search contacts by name, email, or phone"""
    print("\n🔍 SEARCH CONTACTS")
    print("-" * 30)
    query = input("Enter search term (name, email, or phone): ").strip()
    
    if not query:
        print("❌ Please enter a search term!")
        return
    
    cur.execute("""
        SELECT DISTINCT c.id, c.name, p.phone, c.email, c.birthday, g.name, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.name ILIKE %s
           OR c.email ILIKE %s
           OR p.phone ILIKE %s
        ORDER BY c.name
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    
    rows = cur.fetchall()
    
    if rows:
        print(f"\n📋 Found {len(rows)} contact(s):")
        print_rows(rows)
    else:
        print("❌ No contacts found!")

def delete_contact():
    """Delete a contact"""
    show_all_contacts()
    
    print("\n🗑️  DELETE CONTACT")
    print("-" * 30)
    print("How would you like to delete?")
    print("1. By name")
    print("2. By phone number")
    
    choice = input("\nYour choice (1-2): ").strip()
    
    try:
        if choice == "1":
            name = input("Enter contact name: ").strip()
            cur.execute("SELECT id, name FROM contacts WHERE name ILIKE %s", (f"%{name}%",))
            contacts = cur.fetchall()
            
            if not contacts:
                print("❌ Contact not found!")
                return
            
            if len(contacts) > 1:
                print("\nMultiple contacts found:")
                for idx, (cid, cname) in enumerate(contacts, 1):
                    print(f"  {idx}. {cname}")
                contact_choice = int(input("Choose contact number: ")) - 1
                contact_id = contacts[contact_choice][0]
            else:
                contact_id = contacts[0][0]
            
            cur.execute("DELETE FROM contacts WHERE id = %s RETURNING id", (contact_id,))
            if cur.fetchone():
                print("✅ Contact deleted successfully!")
            
        elif choice == "2":
            phone = input("Enter phone number: ").strip()
            cur.execute("""
                SELECT c.id, c.name FROM contacts c
                JOIN phones p ON p.contact_id = c.id
                WHERE p.phone = %s
            """, (phone,))
            contact = cur.fetchone()
            
            if contact:
                cur.execute("DELETE FROM contacts WHERE id = %s", (contact[0],))
                print(f"✅ Contact '{contact[1]}' deleted successfully!")
            else:
                print("❌ Contact with this phone number not found!")
        else:
            print("❌ Invalid choice!")
            return
        
        conn.commit()
        print("\n📋 Remaining contacts:")
        show_all_contacts()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

def show_all_contacts():
    """Display all contacts"""
    cur.execute("""
        SELECT DISTINCT c.id, c.name, p.phone, c.email, c.birthday, g.name, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        ORDER BY c.name
    """)
    rows = cur.fetchall()
    
    if rows:
        print(f"\n📋 ALL CONTACTS ({len(rows)} total)")
        print_rows(rows)
    else:
        print("\n📋 No contacts found!")

def print_rows(rows):
    """Display query results in table format"""
    if not rows:
        print("❌ No data found!")
        return
    
    print(f"\n{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25} {'Birthday':<12} {'Group':<10} {'Type':<8}")
    print("-" * 105)
    for row in rows:
        id_val = row[0] if row[0] else ''
        name = (row[1] or '')[:20]
        phone = (row[2] or '')[:15]
        email = (row[3] or '')[:25]
        birthday = str(row[4])[:12] if row[4] else '-'
        group = (row[5] or 'None')[:10]
        ptype = (row[6] or 'mobile')[:8]
        print(f"{id_val:<5} {name:<20} {phone:<15} {email:<25} {birthday:<12} {group:<10} {ptype:<8}")

# Main menu
def main():
    """Main program loop"""
    print("\n" + "=" * 55)
    print("📞 WELCOME TO PHONEBOOK APPLICATION")
    print("=" * 55)
    
    try:
        while True:
            print("\n" + "=" * 55)
            print("MAIN MENU")
            print("=" * 55)
            print("1. 📥 Import from CSV file")
            print("2. ➕ Add contact manually")
            print("3. ✏️  Update contact")
            print("4. 🔍 Search contacts")
            print("5. 🗑️  Delete contact")
            print("6. 📋 Show all contacts")
            print("0. 🚪 Exit")
            print("-" * 55)
            
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Thank you for using PhoneBook! Goodbye!")
                break
            elif choice == "1":
                insert_from_csv()
            elif choice == "2":
                insert_from_console()
            elif choice == "3":
                update_contact()
            elif choice == "4":
                search_contacts()
            elif choice == "5":
                delete_contact()
            elif choice == "6":
                show_all_contacts()
            else:
                print("❌ Invalid choice! Please enter a number between 0 and 6.")
    
    except KeyboardInterrupt:
        print("\n⏸ Program interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        cur.close()
        conn.close()
        print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main()