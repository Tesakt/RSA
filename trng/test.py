import matplotlib.pyplot as plt
import numpy as np

def calculate_entropy(data):
    _, counts = np.unique(data, return_counts=True)
    probabilities = counts / len(data)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy

def test_bit_randomness(file_path):
    # Otwieramy plik i odczytujemy zawartość jako dane binarne
    with open(file_path, 'rb') as file:
        binary_data = file.read()

    # Konwertujemy dane binarne na listę intów
    integers = [int(byte) for byte in binary_data]

    # Tworzymy histogram
    plt.hist(integers, bins=range(256), edgecolor='black')
    plt.title('Histogram sekwencji bajtów')
    plt.xlabel('Wartość bajta')
    plt.ylabel('Liczba wystąpień')
    plt.show()

    # Obliczamy entropię bitową
    entropy = calculate_entropy(integers)
    print("Bit entropy:", entropy)

if __name__ == '__main__':
    # Testujemy funkcję dla plików extractor_bites.bin i random_sequence.bin
    test_bit_randomness('trng/extractor_bites.bin')
    test_bit_randomness('trng/random_sequence.bin')
