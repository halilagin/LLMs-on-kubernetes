import os
from functools import partial
from pathlib import Path

import psycopg2
import ray
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pgvector.psycopg2 import register_vector
from ray.data import ActorPoolStrategy

from rag.config import EFS_DIR, EMBEDDING_DIMENSIONS
from rag.data import extract_sections
from rag.embed import EmbedChunks
from rag.utils import execute_bash


class StoreResults:
    def __call__(self, batch):
        with psycopg2.connect(os.environ["DB_CONNECTION_STRING"]) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                for text, source, embedding in zip(
                    batch["text"], batch["source"], batch["embeddings"]
                ):
                    cur.execute(
                        "INSERT INTO document (text, source, embedding) VALUES (%s, %s, %s)",
                        (
                            text,
                            source,
                            embedding,
                        ),
                    )
        return {}


def chunk_section(section, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.create_documents(
        texts=[section["text"]], metadatas=[{"source": section["source"]}]
    )
    return [{"text": chunk.page_content, "source": chunk.metadata["source"]} for chunk in chunks]


def set_index(embedding_model_name, chunk_size, chunk_overlap, docs_dir):
    # Drop current Vector DB and prepare for new one
    execute_bash(f'psql "{os.environ["DB_CONNECTION_STRING"]}" -c "DROP TABLE document;"')
    execute_bash(
        f"sudo -u postgres psql -f ../migrations/vector-{EMBEDDING_DIMENSIONS[embedding_model_name]}.sql"
    )
    SQL_DUMP_FP = Path(
        EFS_DIR,
        "sql_dumps",
        f"{embedding_model_name.split('/')[-1]}_{chunk_size}_{chunk_overlap}.sql",
    )

    # Vector DB
    if SQL_DUMP_FP.exists():  # Load from SQL dump
        execute_bash(f'psql "{os.environ["DB_CONNECTION_STRING"]}" -f {SQL_DUMP_FP}')
    else:  # Create new index
        # Sections
        ds = ray.data.from_items(
            [{"path": path} for path in docs_dir.rglob("*.html") if not path.is_dir()]
        )
        sections_ds = ds.flat_map(extract_sections)

        # Create chunks dataset
        chunks_ds = sections_ds.flat_map(
            partial(chunk_section, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )

        # Embed chunks
        embedded_chunks = chunks_ds.map_batches(
            EmbedChunks,
            fn_constructor_kwargs={"model_name": embedding_model_name},
            batch_size=100,
            num_gpus=1,
            compute=ActorPoolStrategy(size=2),
        )

        # Index data
        embedded_chunks.map_batches(
            StoreResults,
            batch_size=128,
            num_cpus=1,
            compute=ActorPoolStrategy(size=28),
        ).count()

        # Save to SQL dump
        execute_bash(f"sudo -u postgres pg_dump -c > {SQL_DUMP_FP}")


def load_index(embedding_model_name, chunk_size, chunk_overlap):
    # Drop current Vector DB and prepare for new one
    execute_bash(f'psql "{os.environ["DB_CONNECTION_STRING"]}" -c "DROP TABLE document;"')
    execute_bash(
        f"sudo -u postgres psql -f ../migrations/vector-{EMBEDDING_DIMENSIONS[embedding_model_name]}.sql"
    )
    SQL_DUMP_FP = Path(
        EFS_DIR,
        "sql_dumps",
        f"{embedding_model_name.split('/')[-1]}_{chunk_size}_{chunk_overlap}.sql",
    )

    # Load vector DB
    if SQL_DUMP_FP.exists():  # Load from SQL dump
        execute_bash(f'psql "{os.environ["DB_CONNECTION_STRING"]}" -f {SQL_DUMP_FP}')
    else:
        raise Exception(f"{SQL_DUMP_FP} does not exist!")
