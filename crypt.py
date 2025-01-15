def menu():
    print("Choisissez l'algorithme de cryptage:")
    print("1. Chiffrement de César")
    print("2. Chiffrement de Vigenère")
    print("3. Chiffrement Affine")
    print("4. Chiffrement de Hill")
    return input("Entrez le numéro de votre choix: ")

def obtenir_cle_cesar():
    while True:
        try:
            cle = int(input("Entrez la clé (un entier): "))
            return cle
        except ValueError:
            print("Veuillez entrer un entier valide.")

def obtenir_cle_vigenere():
    return input("Entrez la clé (un mot): ")

def obtenir_cles_affine():
    while True:
        try:
            a = int(input("Entrez la clé 'a' (un entier): "))
            b = int(input("Entrez la clé 'b' (un entier): "))
            if a % 2 == 0 or a % 13 == 0:
                print("La clé 'a' doit être co-prime avec 26. Veuillez réessayer.")
            else:
                return a, b
        except ValueError:
            print("Veuillez entrer des entiers valides.")

def obtenir_cle_hill():
    import numpy as np
    while True:
        try:
            cle = input("Entrez la clé (matrice 2x2, séparée par des espaces): ")
            elements = list(map(int, cle.split()))
            if len(elements) != 4:
                print("La clé doit contenir 4 éléments.")
            else:
                matrice = np.array(elements).reshape(2, 2)
                return matrice
        except ValueError:
            print("Veuillez entrer des entiers valides.")

def choisir_action():
    print("Voulez-vous chiffrer ou déchiffrer?")
    print("1. Chiffrer")
    print("2. Déchiffrer")
    return input("Entrez le numéro de votre choix: ")

def encrypt_cesar(texte, cle):
    resultat = ""
    for char in texte:
        if char.isupper():
            resultat += chr((ord(char) + cle - 65) % 26 + 65)
        elif char.islower():
            resultat += chr((ord(char) + cle - 97) % 26 + 97)
        else:
            resultat += char
    return resultat

def decrypt_cesar(texte, cle):
    return encrypt_cesar(texte, -cle)

def generate_key_vigenere(texte, cle):
    cle = list(cle)
    if len(texte) == len(cle):
        return cle
    else:
        for i in range(len(texte) - len(cle)):
            cle.append(cle[i % len(cle)])
    return "".join(cle)

def encrypt_vigenere(texte, cle):
    texte_chiffre = []
    cle = generate_key_vigenere(texte, cle)
    for i in range(len(texte)):
        char = texte[i]
        if char.isupper():
            texte_chiffre.append(chr((ord(char) + ord(cle[i]) - 2 * 65) % 26 + 65))
        elif char.islower():
            texte_chiffre.append(chr((ord(char) + ord(cle[i]) - 2 * 97) % 26 + 97))
        else:
            texte_chiffre.append(char)
    return "".join(texte_chiffre)

def decrypt_vigenere(texte_chiffre, cle):
    texte_dechiffre = []
    cle = generate_key_vigenere(texte_chiffre, cle)
    for i in range(len(texte_chiffre)):
        char = texte_chiffre[i]
        if char.isupper():
            texte_dechiffre.append(chr((ord(char) - ord(cle[i]) + 26) % 26 + 65))
        elif char.islower():
            texte_dechiffre.append(chr((ord(char) - ord(cle[i]) + 26) % 26 + 97))
        else:
            texte_dechiffre.append(char)
    return "".join(texte_dechiffre)

def encrypt_affine(texte, a, b):
    resultat = ""
    for char in texte:
        if char.isupper():
            resultat += chr(((a * (ord(char) - 65) + b) % 26) + 65)
        elif char.islower():
            resultat += chr(((a * (ord(char) - 97) + b) % 26) + 97)
        else:
            resultat += char
    return resultat

def decrypt_affine(texte, a, b):
    resultat = ""
    a_inv = pow(a, -1, 26)
    for char in texte:
        if char.isupper():
            resultat += chr(((a_inv * (ord(char) - 65 - b)) % 26) + 65)
        elif char.islower():
            resultat += chr(((a_inv * (ord(char) - 97 - b)) % 26) + 97)
        else:
            resultat += char
    return resultat

def encrypt_hill(texte, matrice_cle):
    import numpy as np
    n = matrice_cle.shape[0]
    texte = texte.replace(" ", "").upper()
    texte = [ord(char) - ord('A') for char in texte]
    while len(texte) % n != 0:
        texte.append(ord('X') - ord('A'))
    texte_matrice = np.array(texte).reshape(-1, n).T
    matrice_chiffree = np.dot(matrice_cle, texte_matrice) % 26
    texte_chiffre = "".join(chr(int(num) + ord('A')) for num in matrice_chiffree.T.flatten())
    return texte_chiffre

def decrypt_hill(texte_chiffre, matrice_cle):
    import numpy as np
    n = matrice_cle.shape[0]
    texte_chiffre = texte_chiffre.replace(" ", "").upper()
    texte_chiffre = [ord(char) - ord('A') for char in texte_chiffre]
    matrice_chiffree = np.array(texte_chiffre).reshape(-1, n).T
    matrice_cle_inv = mod_matrix_inv(matrice_cle, 26)
    matrice_dechiffree = np.dot(matrice_cle_inv, matrice_chiffree) % 26
    texte_dechiffre = "".join(chr(int(num) + ord('A')) for num in matrice_dechiffree.T.flatten())
    return texte_dechiffre

def mod_matrix_inv(matrix, modulus):
    import numpy as np
    det = int(np.round(np.linalg.det(matrix)))
    det_inv = pow(det, -1, modulus)
    matrix_modulus_inv = det_inv * np.round(det * np.linalg.inv(matrix)).astype(int) % modulus
    return matrix_modulus_inv

def main():
    choix = menu()

    if choix == '1':
        cle = obtenir_cle_cesar()
        action = choisir_action()
        texte = input("Entrez le texte: ")
        if action == '1':
            print("Texte chiffré:", encrypt_cesar(texte, cle))
        elif action == '2':
            print("Texte déchiffré:", decrypt_cesar(texte, cle))
    elif choix == '2':
        cle = obtenir_cle_vigenere()
        action = choisir_action()
        texte = input("Entrez le texte: ")
        if action == '1':
            print("Texte chiffré:", encrypt_vigenere(texte, cle))
        elif action == '2':
            print("Texte déchiffré:", decrypt_vigenere(texte, cle))
    elif choix == '3':
        a, b = obtenir_cles_affine()
        action = choisir_action()
        texte = input("Entrez le texte: ")
        if action == '1':
            print("Texte chiffré:", encrypt_affine(texte, a, b))
        elif action == '2':
            print("Texte déchiffré:", decrypt_affine(texte, a, b))
    elif choix == '4':
        matrice_cle = obtenir_cle_hill()
        action = choisir_action()
        texte = input("Entrez le texte: ")
        if action == '1':
            print("Texte chiffré:", encrypt_hill(texte, matrice_cle))
        elif action == '2':
            print("Texte déchiffré:", decrypt_hill(texte, matrice_cle))
    else:
        print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()
