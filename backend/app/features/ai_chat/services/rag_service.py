"""
RAG (Retrieval-Augmented Generation) service.
Loads CV data into ChromaDB, retrieves relevant context for user queries.
"""

import json
import logging
from pathlib import Path

import chromadb
import yaml

from app.config import settings

logger = logging.getLogger(__name__)

_collection = None


def _get_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection (singleton)."""
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.Client()  # In-memory for development; use PersistentClient for prod
    _collection = client.get_or_create_collection(
        name="portfolio_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    # Index knowledge base if collection is empty
    if _collection.count() == 0:
        _index_knowledge_base()

    return _collection


def _index_knowledge_base() -> None:
    """Load CV data and skills matrix into ChromaDB."""
    knowledge_dir = Path(settings.knowledge_base_dir)
    documents = []
    metadatas = []
    ids = []

    # Load cv_data.json
    cv_path = knowledge_dir / "cv_data.json"
    if cv_path.exists():
        cv_data = json.loads(cv_path.read_text())

        # Personal info
        personal = cv_data.get("personal", {})
        doc = (
            f"Name: {personal.get('full_name', '')}. "
            f"Title: {personal.get('headline', '')}. "
            f"Summary: {personal.get('summary', '')}. "
            f"Location: {personal.get('location', '')}."
        )
        documents.append(doc)
        metadatas.append({"source": "cv", "section": "personal"})
        ids.append("personal-info")

        # Skills
        for i, skill in enumerate(cv_data.get("skills", [])):
            doc = f"Skill: {skill['name']} (Category: {skill['category']}, Level: {skill['level']}/100)"
            documents.append(doc)
            metadatas.append({"source": "cv", "section": "skills", "category": skill["category"]})
            ids.append(f"skill-{i}")

        # Experience
        for i, exp in enumerate(cv_data.get("experience", [])):
            doc = (
                f"Experience at {exp['company']} as {exp['role']} "
                f"({exp['start_date']} to {exp['end_date']}): {exp['description']}"
            )
            documents.append(doc)
            metadatas.append({"source": "cv", "section": "experience"})
            ids.append(f"experience-{i}")

        # Education
        for i, edu in enumerate(cv_data.get("education", [])):
            doc = (
                f"Education: {edu['degree']} in {edu.get('field', '')} "
                f"at {edu['institution']} ({edu['start_date']} - {edu['end_date']})"
            )
            documents.append(doc)
            metadatas.append({"source": "cv", "section": "education"})
            ids.append(f"education-{i}")

        # Projects
        for i, proj in enumerate(cv_data.get("projects", [])):
            techs = ", ".join(proj.get("technologies", []))
            doc = f"Project: {proj['title']}. {proj['description']} Technologies: {techs}"
            documents.append(doc)
            metadatas.append({"source": "cv", "section": "projects"})
            ids.append(f"project-{i}")

        # Languages
        langs = cv_data.get("languages", [])
        if langs:
            doc = f"Languages spoken: {', '.join(langs)}"
            documents.append(doc)
            metadatas.append({"source": "cv", "section": "languages"})
            ids.append("languages")

    # Load skills_matrix.yaml
    skills_path = knowledge_dir / "skills_matrix.yaml"
    if skills_path.exists():
        skills_data = yaml.safe_load(skills_path.read_text())
        idx = 0
        for category, skills in skills_data.items():
            for skill_name, skill_info in skills.items():
                if isinstance(skill_info, dict):
                    evidence = skill_info.get("evidence", [])
                    desc = skill_info.get("description", "")
                    level = skill_info.get("level", "")
                    evidence_text = "; ".join(evidence) if evidence else ""
                    doc = (
                        f"Detailed skill: {skill_name} ({category}). "
                        f"{'Level: ' + str(level) + '/100. ' if level else ''}"
                        f"{'Description: ' + desc + '. ' if desc else ''}"
                        f"Evidence: {evidence_text}"
                    )
                    documents.append(doc)
                    metadatas.append({"source": "skills_matrix", "section": category})
                    ids.append(f"matrix-{category}-{idx}")
                    idx += 1

    if documents:
        _collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info(f"Indexed {len(documents)} documents into ChromaDB")


def retrieve_context(query: str, n_results: int = 5) -> str:
    """Retrieve relevant context from the knowledge base for a user query."""
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=n_results)

    if not results["documents"] or not results["documents"][0]:
        return "No specific information found about this topic."

    context_parts = results["documents"][0]
    return "\n\n".join(context_parts)
