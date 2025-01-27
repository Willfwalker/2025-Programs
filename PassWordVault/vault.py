import sqlite3
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class PasswordVault:
    def __init__(self, master_password):
        # Initialize database and encryption
        self.conn = sqlite3.connect('password_vault.db')
        self.cursor = self.conn.cursor()
        self.setup_database()
        self.setup_encryption(master_password)

    def setup_database(self):
        # Create passwords table if it doesn't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def setup_encryption(self, master_password):
        # Generate encryption key from master password
        salt = b'salt_'  # In production, use a secure random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.fernet = Fernet(key)

    def add_password(self, service, username, password):
        # Encrypt and store password
        encrypted_password = self.fernet.encrypt(password.encode())
        self.cursor.execute('''
        INSERT INTO passwords (service, username, encrypted_password)
        VALUES (?, ?, ?)
        ''', (service, username, encrypted_password))
        self.conn.commit()

    def get_password(self, service, username):
        # Retrieve and decrypt password
        self.cursor.execute('''
        SELECT encrypted_password FROM passwords 
        WHERE service = ? AND username = ?
        ''', (service, username))
        result = self.cursor.fetchone()
        if result:
            decrypted_password = self.fernet.decrypt(result[0])
            return decrypted_password.decode()
        return None

    def list_services(self):
        # List all stored services and usernames
        self.cursor.execute('SELECT service, username FROM passwords')
        return self.cursor.fetchall()

    def delete_password(self, service, username):
        # Delete a stored password
        self.cursor.execute('''
        DELETE FROM passwords 
        WHERE service = ? AND username = ?
        ''', (service, username))
        self.conn.commit()

    def __del__(self):
        # Close database connection
        self.conn.close()

# Example usage
def main():
    # Create vault with master password
    master_password = input("Enter master password: ")
    vault = PasswordVault(master_password)
    
    while True:
        print("\n=== Password Vault Menu ===")
        print("1. Add password")
        print("2. Get password")
        print("3. List all services")
        print("4. Delete password")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            vault.add_password(service, username, password)
            print("Password added successfully!")
            
        elif choice == "2":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            password = vault.get_password(service, username)
            if password:
                print(f"Password: {password}")
            else:
                print("Password not found!")
                
        elif choice == "3":
            print("\nStored services:")
            services = vault.list_services()
            if services:
                for service, username in services:
                    print(f"Service: {service}, Username: {username}")
            else:
                print("No passwords stored yet!")
                
        elif choice == "4":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            vault.delete_password(service, username)
            print("Password deleted successfully!")
            
        elif choice == "5":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
