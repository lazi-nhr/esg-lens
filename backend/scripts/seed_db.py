"""Build PostgreSQL database by loading PDF documents and creating embeddings."""
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from app.db.connection import get_db_connection, init_db
from app.db.repositories.documents_repo import DocumentsRepository
from app.retrieval.embedder import create_embedding
from app.db.parser import parse_pdf_to_doc
from app.db.chunker import chunk_document

# Sample ESG documents for testing (if no PDFs provided)
SAMPLE_DOCS = {
    "Apple": [
        "Apple is committed to environmental responsibility and carbon neutrality by 2030. "
        "The company has shifted to 100% renewable energy for all of its facilities worldwide. "
        "Apple's supply chain is being transformed to eliminate emissions.",
        
        "Apple's water management initiatives focus on reducing consumption by 50% by 2030. "
        "The company invests in water conservation projects in manufacturing regions. "
        "Recycled water is used extensively in manufacturing processes.",
    ],
    "Microsoft": [
        "Microsoft aims to be carbon negative by 2030 and remove all historical emissions by 2050. "
        "The company invests in renewable energy projects across multiple continents. "
        "Microsoft's cloud infrastructure runs on 100% renewable energy.",
        
        "Microsoft is committed to circular economy principles and zero waste manufacturing. "
        "The company designs products with sustainability and recyclability in mind. "
        "Extended producer responsibility programs help manage end-of-life products.",
    ],
    "Tesla": [
        "Tesla manufactures vehicles using renewable energy sources. "
        "The company's factories operate on 100% renewable electricity in most locations. "
        "Tesla is expanding battery recycling to reduce material waste.",
        
        "Tesla's supply chain focuses on ethically sourced minerals. "
        "The company works to minimize environmental impact of lithium extraction. "
        "Partnerships with mining companies ensure responsible sourcing practices.",
    ],
}


def seed_from_samples():
    """Load sample ESG documents into database."""
    print("Loading sample ESG documents into PostgreSQL...")
    conn = get_db_connection()
    try:
        doc_count = 0
        for company, docs in SAMPLE_DOCS.items():
            for i, content in enumerate(docs):
                embedding = create_embedding(content)
                doc_id = DocumentsRepository.add(content, embedding)
                doc_count += 1
                print(f"  ✓ {company} doc {i+1}: ID {doc_id}")
        
        print(f"\n✅ Successfully indexed {doc_count} documents")
        return doc_count
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()


def seed_from_directory(pdf_dir: Path):
    """Load PDF documents from directory into database."""
    print(f"Loading PDF documents from {pdf_dir}...")
    
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return 0
    
    conn = get_db_connection()
    try:
        doc_count = 0
        for pdf_path in pdf_files:
            print(f"  Processing {pdf_path.name}...")
            doc = parse_pdf_to_doc(str(pdf_path))
            
            # Chunk the document
            chunks = chunk_document(
                doc["page_texts"],
                doc["_id"],
                base_tokens=512,
                overlap_tokens=64
            )
            
            for chunk in chunks:
                content = chunk.get("text", "")
                if content.strip():
                    embedding = create_embedding(content)
                    doc_id = DocumentsRepository.add(content, embedding)
                    doc_count += 1
            
            print(f"    → Created {len(chunks)} chunks from {pdf_path.name}")
        
        print(f"\n✅ Successfully indexed {doc_count} chunks from PDFs")
        return doc_count
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Build PostgreSQL RAG database")
    parser.add_argument(
        "--samples",
        action="store_true",
        help="Load sample ESG documents (default)"
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        help="Load PDF documents from directory"
    )
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only initialize database schema (don't load data)"
    )
    
    args = parser.parse_args()
    
    # Always initialize database first
    print("Initializing database...")
    init_db()
    print("✅ Database initialized\n")
    
    if args.init_only:
        return
    
    # Load data
    if args.pdf_dir:
        seed_from_directory(args.pdf_dir)
    else:
        # Default to sample documents
        seed_from_samples()


if __name__ == "__main__":
    main()