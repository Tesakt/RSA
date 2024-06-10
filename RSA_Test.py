import hashlib
import rsa
import sys

# Function to generate SHA-3 hash of a message
def generate_sha3_hash(message):
    sha3_hash = hashlib.sha3_256()
    sha3_hash.update(message)
    return sha3_hash.digest()

# Function to verify a digital signature
def verify_signature(public_key, signature, message_hash):
    try:
        rsa.verify(message_hash, signature, public_key)
        return True
    except rsa.VerificationError:
        return False

# Function to load a key from a file
def load_key_from_file(file_path, key_type):
    with open(file_path, 'rb') as file:
        key_data = file.read()
        if key_type == 'public':
            return rsa.PublicKey.load_pkcs1_openssl_pem(key_data)
        elif key_type == 'private':
            return rsa.PrivateKey.load_pkcs1_openssl_pem(key_data)

# Function to load signature from a file
def load_signature_from_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Main function
def main( messageFileName):

    # Step 3: Message to be signed (read from a PNG file)
    with open('Wiadomosci/'+ messageFileName, 'rb') as file:
        message = file.read()
    
    # Step 4: Generate MD5 hash of the message
    message_hash = generate_sha3_hash(message)
    
    # Step 6: Load keys and signature for verification
    loaded_public_key = load_key_from_file('Odbiorca/public_key.pem', 'public')
    loaded_signature = load_signature_from_file('Nadawca/signature.txt')
    
    # Verify the signature using the loaded public key
    is_valid = verify_signature(loaded_public_key, loaded_signature, message_hash)

    # Display results
    print(f"Test Message Hash: {message_hash.hex()}\n")
    print(f"Test Signature: {loaded_signature.hex()}\n")
    print(f"Test Signature is valid: {is_valid}\n")

# Run the main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python RSA_TEST.py <messageFileName>")
        sys.exit(1)
    
    messageFileName = sys.argv[1]
    main(messageFileName)
