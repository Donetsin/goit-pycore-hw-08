'''this module provides OOP model of the note helper'''
import re
import pickle
from collections import UserDict
from datetime import datetime as dt, timedelta as td
from colorama import Style, Fore

def input_error(func):
    '''function process different kind of errors'''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as ke:
            return Fore.RED + str(ke) + Style.RESET_ALL
        except IndexError as ie:
            return Fore.RED + str(ie) + Style.RESET_ALL
        except ValueError as ve:
            return Fore.RED + str(ve) + Style.RESET_ALL
        except Exception as e:
            return Fore.RED + str(e) + Style.RESET_ALL
    return wrapper

def parse_input(user_input):
    '''input value parser'''
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Field:
    '''documentation for the class Field'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    '''documentation for the class Name'''
    pass

class Phone(Field):
    '''documentation for the class Phone'''
    def __init__(self, value):
        super().__init__(value)
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Error. Phone number must be 10 digits")

class Birthday(Field):
    '''documentation for the class Birthday'''
    def __init__(self, value):
        super().__init__(value)
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            self.value = dt.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def to_this_year(self) -> dt:
        '''returns Birthday for this year'''
        return self.value.replace(year = dt.now().year)

class Record:
    '''documentation for the class Record'''
    def __init__(self, person_name):
        self.name = Name(person_name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phone(s): {', '.join(number for number in self.phones)}"

    def add_phone(self, phone):
        '''add phone number to record line'''
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def del_phone(self, phone):
        '''delete phone number from record line'''
        self.phones = [number for number in self.phones if number.value != phone]

    def edit_phone(self, old_phone, new_phone):
        '''edit phone number in record line'''
       # self.phones = list(map(lambda x: x.replace(old_phone, new_phone), self.phones))
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return True
            return False

    def find_phone(self, phone):
        '''return phone number from record line'''
        for number in self.phones:
            if number == phone:
                return number
        raise IndexError("Phone number is not found.")

    def add_birthday(self, birthday):
        '''add birthday date to record line'''     
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    '''documentation for the class AddressBook'''
    def add_record(self, record):
        '''add record to address book'''
        self.data[record.name.value] = record

    def find(self, name):
        '''return record from address book'''
        return self.data.get(name)

    def delete(self, name):
        '''delete record from address book'''
        if name in self.data:
            del self.data[name]

    def return_all(self):
        '''Prints all contacts line by line'''
        prntstr = ""
        for name, record in self.data.items():
            prntstr += str(f"Name: {name}, Phone(s): {', '.join(phone.value for phone in record.phones)}, "\
                  f"Birthday: {record.birthday.value.strftime('%d.%m.%Y') if record.birthday else 'None'}\n")
        return prntstr

    def get_upcoming_birthdays(self):
        """Returns list of employee Birthday during next 7 days"""
        current_date = dt.today().date()
        birthdays = []

        for record in self.data.values():
            birthday = record.birthday
            if birthday:
                this_year_birthday = birthday.to_this_year().date()

                # birthday has already passed
                if this_year_birthday < current_date:
                    # use next year birthday
                    this_year_birthday = this_year_birthday.replace(year = current_date.year + 1)

                days_delta = (this_year_birthday - current_date).days
                # check if birthday in next 7 days
                if 0 <= days_delta <= 7:
                    # if Saturday or Sunday
                    if this_year_birthday.weekday() >= 5:
                        # move to Monday
                        this_year_birthday += td(days = 7 - this_year_birthday.weekday())

                    # populate birthday greetings
                    birthdays.append({"name": record.name.value, "congratulation_date": this_year_birthday.strftime("%d.%m.%Y")})

        line = [f"name: {bd['name']},  congratulation date: {bd['congratulation_date']}" for bd in birthdays]
        print(*line, sep = "\n")

@input_error
def add_birthday(args, book):
    '''add birthday to contact'''    
    name, birthday_str = args
    record = book.get(name)
    if not record:
        raise ValueError("Contact not found.")
    record.add_birthday(birthday_str)
    return Fore.GREEN + f"Birthday added for {name}" + Style.RESET_ALL

@input_error
def show_birthday(args, book):
    '''show birthday of a contact'''
    name = args[0]
    record = book.get(name)
    if not record or not record.birthday:
        raise ValueError("Birthday not found.")
    return f"Birthday of {name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(book):
    '''show all upcoming birthdays'''
    return book.get_upcoming_birthdays()

@input_error
def add_contact(args, book):
    '''add new contact'''
    if len(args) < 2:
        raise IndexError("Invalid input. Please use the format: add [name] [phone]")
    record = Record(args[0])
    record.add_phone(args[1])
    book.add_record(record)
    return Fore.GREEN + "Contact added." + Style.RESET_ALL

@input_error
def update_contact(args, book):
    '''contacts updater'''
    if len(args) != 3:
        raise IndexError("Invalid input. Please use the format: add [name] [old phone] [new phone]")

    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.edit_phone(old_phone, new_phone):
        book["phone"] = new_phone
        return Fore.GREEN + "Contact updated." + Style.RESET_ALL

    raise KeyError("Contact not found.")

@input_error
def get_phone(args, book):
    '''show phone by contact name'''
    if len(args) != 1:
        raise IndexError("Invalid input. Please use the format: phone [name]")
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    raise KeyError("Contact not found.")

def print_all(book):
    '''return all list of contacts'''
    print(book.return_all())

def save_data(book, filename="addressbook.pkl"):
    '''save data to file'''
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    '''restore data from file'''
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    '''entry point'''    
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        if command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(update_contact(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            print_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print(Fore.RED + "Invalid command." + Style.RESET_ALL)

if __name__ == "__main__":
    main()

