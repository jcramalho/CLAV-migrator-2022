import re 
frase = 'Era uma vez "El Espacio"...'
frase = re.sub(r'\"', "\\\"", frase)
print(frase)