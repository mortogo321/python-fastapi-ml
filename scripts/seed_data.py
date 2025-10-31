"""
Seed script to populate the database with sample documents.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.base import AsyncSessionLocal
from app.services.document_service import document_service


async def seed_documents():
    """Seed database with sample documents."""

    sample_documents = [
        {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that enables "
                      "systems to learn and improve from experience without being explicitly "
                      "programmed. It focuses on the development of computer programs that can "
                      "access data and use it to learn for themselves.",
            "metadata": "category: AI, level: beginner"
        },
        {
            "title": "FastAPI Framework",
            "content": "FastAPI is a modern, fast (high-performance) web framework for building "
                      "APIs with Python 3.7+ based on standard Python type hints. It is one of "
                      "the fastest Python frameworks available, on par with NodeJS and Go.",
            "metadata": "category: Web Development, level: intermediate"
        },
        {
            "title": "Vector Databases",
            "content": "Vector databases are specialized databases designed to store and query "
                      "high-dimensional vectors efficiently. They are essential for applications "
                      "involving similarity search, recommendation systems, and semantic search.",
            "metadata": "category: Database, level: advanced"
        },
        {
            "title": "Natural Language Processing",
            "content": "Natural Language Processing (NLP) is a branch of AI that helps computers "
                      "understand, interpret and manipulate human language. NLP draws from many "
                      "disciplines, including computer science and computational linguistics.",
            "metadata": "category: AI, level: intermediate"
        },
        {
            "title": "Docker Containers",
            "content": "Docker is a platform for developing, shipping, and running applications "
                      "in containers. Containers allow developers to package an application with "
                      "all its dependencies and ship it as one package.",
            "metadata": "category: DevOps, level: beginner"
        }
    ]

    async with AsyncSessionLocal() as db:
        print("Seeding documents...")

        for doc_data in sample_documents:
            try:
                document = await document_service.create_document(
                    db=db,
                    title=doc_data["title"],
                    content=doc_data["content"],
                    metadata=doc_data["metadata"]
                )
                print(f"Created document: {document.id} - {document.title}")

            except Exception as e:
                print(f"Error creating document '{doc_data['title']}': {e}")

    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_documents())
