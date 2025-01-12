from collections import defaultdict
import os

class KolejkaPriorytetowa:
    def __init__(self):
        self.q = []

    def push(self, item):
        self.q.append(item)
        self._kopup(len(self.q) - 1)

    def pop(self):
        if self.pusty():
            raise IndexError("Pop z pustej kolejki")
        self._swap(0, len(self.q) - 1)
        item = self.q.pop()
        self._heapify_down(0)
        return item

    def pusty(self):
        return len(self.q) == 0

    def _kopup(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.q[index] < self.q[parent]:
            self._swap(index, parent)
            self._kopup(parent)

    def _heapify_down(self, index):
        smol = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < len(self.q) and self.q[left] < self.q[smol]:
            smol = left
        if right < len(self.q) and self.q[right] < self.q[smol]:
            smol = right

        if smol != index:
            self._swap(index, smol)
            self._heapify_down(smol)

    def _swap(self, i, j):
        self.q[i], self.q[j] = self.q[j], self.q[i]

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class KodowanieHuffmana:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}

    def build_fqtable(self, text):
        fq = defaultdict(int)
        for char in text:
            fq[char] += 1
        return fq

    def build_kp(self, fq):
        kp = KolejkaPriorytetowa()
        for char, freq in fq.items():
            node = Node(char, freq)
            kp.push(node)
        return kp

    def build_huffdrzewo(self, kp): #hehe huff drzewo (marichuana)
        while len(kp.q) > 1:
            node1 = kp.pop()
            node2 = kp.pop()

            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            kp.push(merged)

        return kp.pop()

    def build_bob(self, korzen, current_code): #bob budowniczy bo code helper
        if korzen is None:
            return

        if korzen.char is not None:
            self.codes[korzen.char] = current_code
            self.reverse_mapping[current_code] = korzen.char
            return

        self.build_bob(korzen.left, current_code + "0")
        self.build_bob(korzen.right, current_code + "1")

    def build_kod(self, korzen):
        self.build_bob(korzen, "")

    def get_zakodowany(self, text):
        zakodowany_tekst = ""
        for char in text:
            zakodowany_tekst += self.codes[char]
        return zakodowany_tekst

    def add_padd(self, zakodowany_tekst):
        extra_padding = 8 - len(zakodowany_tekst) % 8
        for i in range(extra_padding):
            zakodowany_tekst += "0"

        padded_info = "{0:08b}".format(extra_padding)
        zakodowany_tekst = padded_info + zakodowany_tekst
        return zakodowany_tekst

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Zakodowany teskt nie ma odpowiedniego paddingu")
            exit(0)

        byte_array = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            byte_array.append(int(byte, 2))
        return byte_array

    def kompresja(self, input_path):
        with open(input_path, 'r') as file:
            text = file.read()
            text = text.rstrip()

        fq = self.build_fqtable(text)
        kp = self.build_kp(fq)
        korzen = self.build_huffdrzewo(kp)

        self.build_kod(korzen)

        zakodowany_tekst = self.get_zakodowany(text)
        padded_encoded_text = self.add_padd(zakodowany_tekst)

        outputp = "c" + input_path.split(".")[0] + ".bin"
        with open(outputp, 'wb') as output:
            slownikowy_B = (str(self.codes) + "\n").encode('utf-8')
            output.write(slownikowy_B)
            # Write padded encoded text as binary
            byte_array = self.get_byte_array(padded_encoded_text)
            output.write(byte_array)

        print("Kompresja zakończona.")
        print(f"Nazwa pliku: {outputp}")

    def unaddpadd(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:]
        zakodowany_tekst = padded_encoded_text[:-1 * extra_padding]

        return zakodowany_tekst

    def dekoduj_tekst(self, zakodowany_tekst):
        current_code = ""
        zdekowoany_tekst = ""

        for bit in zakodowany_tekst:
            current_code += bit
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                zdekowoany_tekst += character
                current_code = ""

        return zdekowoany_tekst

    def dekompresja(self, input_path):
        file_name, file_extension = os.path.splitext(input_path)
        outputp = file_name.replace(file_name[0], "d", 1) + ".txt"

        with open(input_path, 'rb') as file:
            # Read the dictionary from the first part
            slownikowy_B = b""
            while True:
                byte = file.read(1)
                if byte == b"\n":
                    break
                slownikowy_B += byte
            self.codes = eval(slownikowy_B.decode('utf-8'))
            self.reverse_mapping = {v: k for k, v in self.codes.items()}

            # Read the encoded text as binary
            bit_string = ""
            byte = file.read(1)
            while byte:
                byte = ord(byte)
                bit = bin(byte)[2:].rjust(8, '0')
                bit_string += bit
                byte = file.read(1)

        zakodowany_tekst = self.unaddpadd(bit_string)

        zdekompresowany_tekst = self.dekoduj_tekst(zakodowany_tekst)

        with open(outputp, 'w') as output:
            output.write(zdekompresowany_tekst)

        print("Dekompresja zakończona.")
        print(f"Nazwa pliku: {outputp}")


if __name__ == "__main__":
    try:
        CorD = int(input("Podaj opcję:\nAby kompresować wybierz: 1,\nAby zdekompresować wybierz: 2.\n"))
        huffman = KodowanieHuffmana()
        if CorD == 1:
            input_file = input("Nazwa pliku do kompresji (UWAGA! plik musi być w formacie .txt, wpisując nazwę nie trzeba dodawać rozszerzenia pliku):\n")
            huffman.kompresja(input_file + ".txt")
        elif CorD == 2:
            input_file = input("Nazwa pliku do dekompresji (UWAGA! plik musi być w formacie .bin, wpisując nazwę nie trzeba dodawać rozszerzenia pliku):\n")
            huffman.dekompresja(input_file.split(".")[0] + ".bin")
        else:
            raise ValueError("Nieprawidłowa opcja. Wybierz 1 lub 2.")
    except ValueError as e:
        print(f"BRUH: {e}")
