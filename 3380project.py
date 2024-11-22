import mysql.connector
from mysql.connector import Error
import smtplib
from decimal import Decimal

def get_password_from_file(filename='pw.txt'):
    try:
        with open(filename, 'r') as file:
            return file.read().strip() 
    except FileNotFoundError:
        print(f"Password file '{filename}' not found. Ensure it exists in the same directory.")
        return None

def connect_to_db():
    password = get_password_from_file()
    if not password:
        return None  

    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='apartment_schema',
            user='root',
            password=password
        )
        return connection
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None

def pay_rent(tenant_id, tenant_email, apartment_rent, payment_amount):
    connection = connect_to_db()
    if not connection:
        return

    try:
        cursor = connection.cursor()
    
        cursor.execute("SELECT Rent FROM Apartment WHERE Unit_No = (SELECT Unit_No FROM CurrentTenant WHERE ID = %s)", (tenant_id,))
        rent = cursor.fetchone()
        if not rent:
            print("Tenant ID not found.")
            return

        rent = rent[0] 
        if rent <= Decimal('0.00'):
            print("No rent is owed.")
            return

        payment_amount = Decimal(str(payment_amount))
        new_rent = rent - payment_amount
        cursor.execute("UPDATE Apartment SET Rent = %s WHERE Unit_No = (SELECT Unit_No FROM CurrentTenant WHERE ID = %s)", (new_rent, tenant_id))
        connection.commit()

        #This is where I would send an email confirmation, but all the synthetic emails are fake

        print("Rent payment processed successfully.")
    except Error as e:
        print("Error:", e)
    finally:
        connection.close()

def apply_for_tenancy(potential_tenant_id):
    connection = connect_to_db()
    if not connection:
        return

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PotentialTenant WHERE ID = %s", (potential_tenant_id,))
        potential_tenant = cursor.fetchone()
        if not potential_tenant:
            print("Potential Tenant ID not found.")
            return

        background_check_passed = True  #Simulate background check, I'm not gonna do a for real background check on a fake person
        if not background_check_passed:
            print("Background check failed.")
            return

        cursor.execute("""
            INSERT INTO CurrentTenant (ID, Fname, Lname, Phone_No, Email, Unit_No)
            VALUES (%s, %s, %s, %s, %s, NULL)
        """, potential_tenant)
        connection.commit()

        print("Potential tenant successfully converted into current tenant.")
    except Error as e:
        print("Error:", e)
    finally:
        connection.close()

def evict_tenant(staff_ssn, tenant_id, apartment_number):
    connection = connect_to_db()
    if not connection:
        return

    try:
        cursor = connection.cursor()

        print(f"Staff with SSN {staff_ssn} is assigned to evict tenant {tenant_id} from apartment {apartment_number}.")

        cursor.execute("DELETE FROM CurrentTenant WHERE ID = %s AND Unit_No = %s", (tenant_id, apartment_number))
        connection.commit()

        print("Tenant successfully evicted.")
    except Error as e:
        print("Error:", e)
    finally:
        connection.close()

if __name__ == "__main__":
    while True:
        print("\nMenu:")
        print("1. Pay Rent")
        print("2. Apply for Tenancy")
        print("3. Evict Tenant")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            tenant_id = int(input("Enter Tenant ID: "))
            tenant_email = input("Enter Tenant Email: ")
            apartment_rent = float(input("Enter Apartment Rent: "))
            payment_amount = float(input("Enter Payment Amount: "))
            pay_rent(tenant_id, tenant_email, apartment_rent, payment_amount)
        elif choice == "2":
            potential_tenant_id = int(input("Enter Potential Tenant ID: "))
            apply_for_tenancy(potential_tenant_id)
        elif choice == "3":
            staff_ssn = int(input("Enter Staff SSN: "))
            tenant_id = int(input("Enter Tenant ID: "))
            apartment_number = int(input("Enter Apartment Number: "))
            evict_tenant(staff_ssn, tenant_id, apartment_number)
        elif choice == "4":
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please try again.")