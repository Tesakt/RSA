from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256
import os
import sys
import trng.final as trng

# Function to read TRNG data from a binary file
def read_trng_data(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Function to generate SHA-3 hash of a message
def generate_sha3_hash(message):
    sha3_hash = SHA3_256.new()
    sha3_hash.update(message)
    return sha3_hash.digest()

class CustomRandom:
    def __init__(self):
        self.random_bits = trng.run_TRNG()
        self.index = 0

    def read(self, N):
        # If we run out of random bits, generate more
        if self.index == len(self.random_bits):
            print("Generating more random bits...")
            self.random_bits += trng.run_TRNG()
            
        result = self.random_bits[self.index:self.index + (N*8)]
        self.index += N*8
        
        # Convert the bits to bytes
        bytes_result = bytes(int(''.join(map(str, result[i:i+8])), 2) for i in range(0, len(result), 8))
        return bytes_result

# Function to generate RSA key pair using custom random generator
def generate_rsa_keys():
    custom_random = CustomRandom()
    key = RSA.generate(2048, randfunc=lambda N: custom_random.read(N))
    return key.publickey(), key

# Function to create a digital signature using SHA-3 hash
def create_signature(private_key, message_hash):
    return pkcs1_15.new(private_key).sign(SHA3_256.new(message_hash))

# Function to verify a digital signature using SHA-3 hash
def verify_signature(public_key, signature, message_hash):
    try:
        pkcs1_15.new(public_key).verify(SHA3_256.new(message_hash), signature)
        return True
    except (ValueError, TypeError):
        return False

# Function to save a key to a file
def save_key_to_file(key, file_path, key_type):
    with open(file_path, 'wb') as file:
        if key_type == 'public':
            file.write(key.export_key(format='PEM'))
        elif key_type == 'private':
            file.write(key.export_key(format='PEM'))

# Function to load a key from a file
def load_key_from_file(file_path, key_type):
    with open(file_path, 'rb') as file:
        key_data = file.read()
        if key_type == 'public':
            return RSA.import_key(key_data)
        elif key_type == 'private':
            return RSA.import_key(key_data)

# Function to save signature to a file
def save_signature_to_file(signature, file_path):
    with open(file_path, 'wb') as file:
        file.write(signature)

# Function to load signature from a file
def load_signature_from_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Main function
def main(messageFileName):
    
    # Step 1: Generate RSA keys using TRNG data
    public_key, private_key = generate_rsa_keys()
    
    # Save keys to files
    if not os.path.exists('Nadawca'):
        os.makedirs('Nadawca')
    if not os.path.exists('Odbiorca'):
        os.makedirs('Odbiorca')
    
    save_key_to_file(private_key, 'Nadawca/private_key.pem', 'private')
    save_key_to_file(public_key, 'Odbiorca/public_key.pem', 'public')
    
    # Step 2: Message to be signed (read from a PNG file)
    with open('Wiadomosci/' + messageFileName , 'rb') as file:
        message = file.read()
    
    # Step 3: Generate MD5 hash of the message
    message_hash = generate_sha3_hash(message)
    
    # Step 4: Create digital signature by signing the hash with the private key
    signature = create_signature(private_key, message_hash)
    
    # Save signature to file
    save_signature_to_file(signature, 'Nadawca/signature.txt')
    
    # Step 5: Load keys and signature for verification
    loaded_public_key = load_key_from_file('Odbiorca/public_key.pem', 'public')
    loaded_signature = load_signature_from_file('Nadawca/signature.txt')
    
    # Verify the signature using the loaded public key
    is_valid = verify_signature(loaded_public_key, loaded_signature, message_hash)

    # Display results
    print(f"Original Message Hash: {message_hash.hex()}\n")
    print(f"Signature: {loaded_signature.hex()}\n")
    print(f"Signature is valid: {is_valid}\n")

# Run the main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python RSA_Generator.py <messageFileName>")
        sys.exit(1)
    
    messageFileName = sys.argv[1]
    main(messageFileName)
