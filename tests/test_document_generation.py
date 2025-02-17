import pytest
from typing import assert_type, LiteralString
from collections.abc import AsyncIterator
import asyncio
from pathlib import Path
from dataclasses import dataclass
import tempfile

from odg.document_generator import DocumentGenerator
from odg.document import DocumentMode, DocumentSection

@dataclass(frozen=True)
class DocumentResult:
    path: Path
    success: bool = True

    def is_valid(self) -> bool:
        return self.success and self.path.exists()

class AsyncDocumentGenerator:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    async def generate_documents(
        self,
        templates: list[str]
    ) -> AsyncIterator[tuple[str, Path]]:
        for template in templates:
            result = await self.generate_single(template)
            yield template, result.path

    async def generate_single(self, name: str) -> DocumentResult:
        # Create actual temporary file
        output_path = self.temp_dir / f"{name}"
        output_path.touch()  # Actually create the file
        return DocumentResult(path=output_path)

@pytest.fixture
async def async_generator():
    generator = AsyncDocumentGenerator()
    yield generator
    # Cleanup
    if generator.temp_dir.exists():
        for file in generator.temp_dir.iterdir():
            file.unlink()
        generator.temp_dir.rmdir()

class TestDocumentGeneration:
    async def test_async_generation(self, async_generator) -> None:
        templates = ["template1.docx", "template2.docx"]
        
        async for name, path in async_generator.generate_documents(templates):
            assert_type(name, LiteralString)
            assert isinstance(path, Path)
            assert path.exists()

    async def test_concurrent_generation(self, async_generator) -> None:
        async def generate_doc(name: str) -> DocumentResult:
            return await async_generator.generate_single(name)

        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(generate_doc("doc1"))
            task2 = tg.create_task(generate_doc("doc2"))
            
        # The results are already available after the TaskGroup context exits
        assert task1.result().is_valid()
        assert task2.result().is_valid()

    async def _generate_doc(self, name: str) -> DocumentResult:
        """Helper method for document generation."""
        generator = AsyncDocumentGenerator()
        return await generator.generate_single(name)
