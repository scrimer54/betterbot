from collections import UserDict
from datetime import date, timedelta
import pickle
import functools

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value  

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass  

    def __str__(self):
        return str(self._value)

class Name(Field):
    pass

class Phone(Field):
    def validate(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Phone number must contain 10 digits.")

class Birthday(Field):
    def validate(self, value):
        try:
            date(*map(int, value.split('-')))
        except (TypeError, ValueError):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        phone = Phone(phone)
        self.phones.append(phone)

    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_until_birthday = (next_birthday - today).days
            return days_until_birthday if days_until_birthday >= 0 else 365 + days_until_birthday
        return None

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.load_from_file()

    def load_from_file(self):
        
        try:
            with open(self.file_path, 'rb') as file:
                data = pickle.load(file)
                self.data = data
        except FileNotFoundError:
            self.data = {}

    def save_to_file(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_to_file()

    def delete(self, name):
        del self.data[name]
        self.save_to_file()

    def search(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                results.append(record)
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
        return results
    
contacts = {}

def input_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError):
            return "Error: Invalid input. Try again."

    return wrapper

def hello():
    return "How can I help you?"

@input_error
def add_contact(name, phone, birthday=None):
    contact = Record(name, birthday)
    contact.add_phone(phone)
    contacts[name] = contact
    return f"The contact {name} with the number {phone} has been added."

@input_error
def change_contact(name, new_phone, new_birthday=None):
    contact = contacts[name]
    if new_birthday:
        contact.birthday = Birthday(new_birthday)
    contact.add_phone(new_phone)
    return f"The phone number for {name} has been changed to {new_phone}."

@input_error
def phone_contact(name):
    contact = contacts[name]
    return f"Phone number for {name}: {contact.phones[0].value}"

def show_all_contacts():
    if not contacts:
        return "You have no contacts saved."
    
    result = "List of contacts:\n"
    for name, contact in contacts.items():
        result += f"{contact}\n"
    
    return result.strip()

def main():
    file_path = "address_book_data.pkl"
    address_book = AddressBook(file_path)
    
    print("Welcome to the helper bot!")

    while True:
        user_input = input("Enter the command (or 'exit' to finish): ").lower()

        if user_input == "exit" or user_input == "good bye" or user_input == "close":
            print("Good bye!")
            break
        elif user_input == "hello":
            print(hello())
        elif user_input.startswith("add"):
            _, name, phone, *birthday = user_input.split(maxsplit=3)
            birthday = birthday[0] if birthday else None
            print(add_contact(name, phone, birthday))
            address_book.add_record(contacts[name])
        elif user_input.startswith("change"):
            _, name, new_phone, *new_birthday = user_input.split(maxsplit=3)
            new_birthday = new_birthday[0] if new_birthday else None
            print(change_contact(name, new_phone, new_birthday))
            address_book.save_to_file()
        elif user_input.startswith("phone"):
            _, name = user_input.split(maxsplit=1)
            print(phone_contact(name))
        elif user_input == "show all":
            print(show_all_contacts())
        elif user_input.startswith("search"):
            _, query = user_input.split(maxsplit=1)
            results = address_book.search(query)
            if results:
                print("Search results:")
                for result in results:
                    print(result)
            else:
                print("No matching contacts found.")
        else:
            print("Unknown command. Try again.")
if __name__ == "__main__":
    main()
