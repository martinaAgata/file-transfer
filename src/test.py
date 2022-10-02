fileSeparated = []
file = open("files/Recetario-6.pdf", "rb")

data = file.read(2048)
while data:
    print("hola")
    fileSeparated.append(data)
    data = file.read(2048)

print(len(fileSeparated))