#!/usr/bin/env python3
"""
Script para generar embeddings y crear el vector store
"""

from util.vectorstore_builder import build_vectorstore_simple

if __name__ == "__main__":
    print("🔨 Generando embeddings y creando vector store...")
    vectorstore = build_vectorstore_simple()
    print(f"✅ Vector store creado exitosamente con {vectorstore._collection.count()} documentos")
