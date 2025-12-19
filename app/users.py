def hash_password(password):
    binery_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(binery_password, salt)
    return hash.decode('utf-8')
 
 
def valid_hash(password, hash):
    bin_pwd = password.encode('utf-8')
    bin_hash = hash.encode('utf-8')
    return bcrypt.checkpw(bin_pwd, bin_hash)
 
def register_user():
    user_name = input('enter your user name: ')
    user_pwd = input('enter your password: ')
    hash = hash_password(user_pwd)
    with open('user.txt', 'a') as f:
        f.write(f'{user_name},{hash}\n')
 

def log_in_user(): 
    user_name = input('Enter your user name: ')
    user_pwd = input('Enter your password: ')
    with open('user.txt', 'r') as f:
        users = f.readlines()
    for user in users:
        name, hash = user.strip().split(',')

        if user_name == name:
            return valid_hash(user_pwd, hash)
    return False


def menu():
    print('*'* 30)
    print('*** Welcome to my system ***')
    print('Choose from the following options: ')
    print('1. Register')
    print('2. Log in')
    print('3. EXIT')
    print('*'* 30)


def main():
    while True:
        menu()
        choice = input('> ')
        if choice == '1': 
            register_user()
        elif choice == '2':
           if log_in_user():
               print('You logged in!')
        elif choice =='3':
            print('Good bye!!')
            break