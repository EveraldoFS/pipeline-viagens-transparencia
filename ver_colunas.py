import os
import glob

print("📂 Procurando CSVs...")
print("="*50)

# Procura em toda a estrutura de pastas
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.csv'):
            caminho = os.path.join(root, file)
            print(f"   {caminho}")

print("="*50)