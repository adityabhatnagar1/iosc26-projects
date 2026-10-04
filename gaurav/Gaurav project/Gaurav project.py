"""
Caesar Cipher Project
---------------------
A simple program to encrypt and decrypt text using the Caesar cipher.

Name   : Gaurav
Roll   : 04719051725
Batch  : B1
Course : IIOT (2nd Year)
"""

letters = 'abcdefghijklmnopqrstuvwxyz'
num_letters = len(letters)


def shift_letter(letter, key):
    # check if the letter is uppercase so we can keep it that way
    if letter.isupper():
        letter = letter.lower()
        uppercase = True
    else:
        uppercase = False

    index = letters.find(letter)
    new_index = (index + key) % num_letters

    shifted_letter = letters[new_index]
    if uppercase:
        return shifted_letter.upper()
    else:
        return shifted_letter


def Encrypt(plaintext, key):
    ciphertext = ''
    for letter in plaintext:
        if letter.lower() in letters:
            ciphertext += shift_letter(letter, key)
        else:
            ciphertext += letter
    return ciphertext


def Decrypt(ciphertext, key):
    plaintext = ''
    for letter in ciphertext:
        if letter.lower() in letters:
            plaintext += shift_letter(letter, -key)
        else:
            plaintext += letter
    return plaintext


def get_key():
    # keep asking until the user enters a number from 1 to 25
    while True:
        try:
            key = int(input("ENTER KEY (1-25): "))
            if 1 <= key <= 25:
                return key
            else:
                print("KEY MUST BE 1-25. TRY AGAIN.")
        except ValueError:
            print("ENTER A WHOLE NUMBER. TRY AGAIN.")


def main():
    print()
    print("*****     CAESAR CIPHER PROGRAM     *****")
    print()

    while True:
        print("SELECT OPTION:")
        print("  e - ENCRYPT")
        print("  d - DECRYPT")
        print("  q - QUIT")
        print()

        user_input = input('e/d/q: ').lower()
        print()

        if user_input == 'e':
            print("ENCRYPTION MODE")
            print()
            key = get_key()
            text = input("ENTER TEXT: ")
            ciphertext = Encrypt(text, key)
            print()
            print(f'RESULT: {ciphertext}')
            print()

        elif user_input == 'd':
            print("DECRYPTION MODE")
            print()
            key = get_key()
            text = input("ENTER TEXT: ")
            plaintext = Decrypt(text, key)
            print()
            print(f'RESULT: {plaintext}')
            print()

        elif user_input == 'q':
            print("GOODBYE!")
            break

        else:
            print("INVALID OPTION. CHOOSE e, d OR q.")
            print()


if __name__ == "__main__":
    main()

# This project was learned from the YouTube channel: Fabio Mussani
# Link: https://youtu.be/QYng_rXg5OQ
