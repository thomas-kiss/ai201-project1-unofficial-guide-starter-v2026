"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


_HEADING_RE = re.compile(r"(?m)^##\s+.+$")


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split on `##` section headings.

    city_guides documents are travel guides organized into labelled sections
    (getting there, eating, where to stay, ...). Each section is written as
    one self-contained thought — 84 sections across the 14 guides run 174 to
    709 characters (median 295) — so the heading is a far better chunk
    boundary than any fixed character count: a fixed window either merges two
    unrelated sections or slices through the middle of one.

    Each chunk keeps its heading line, since "the Tuesday market sets up in
    the square from 7am" only means something once you know it's the answer
    to "Eat and drink," not "Getting around."

    A section past config.CHUNK_SIZE is split further with the same
    fixed-window logic as fallback_split, using config.CHUNK_OVERLAP so a
    sentence at the cut point isn't orphaned. Nothing in this corpus is long
    enough to trigger that today; it exists so a future oversized section
    doesn't silently become one giant chunk.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        matches = list(_HEADING_RE.finditer(doc.text))

        if not matches:
            # No headings at all (e.g. the doc's opening paragraph before the
            # first "##"). Treat the whole thing as one section.
            sections = [doc.text]
        else:
            sections = []
            # Anything before the first heading (title, maybe an intro line).
            intro = doc.text[: matches[0].start()].strip()

            heading_sections = []
            for i, match in enumerate(matches):
                end = matches[i + 1].start() if i + 1 < len(matches) else len(doc.text)
                heading_sections.append(doc.text[match.start() : end].strip())

            # Some guides have real intro prose before the first heading;
            # others have only the title line (e.g. "# Walking in the
            # region"), which is a fragment on its own — a heading with no
            # content is not something anyone could answer a question from.
            # 40 characters is comfortably past any bare title line in this
            # corpus but well short of even the shortest real section (174).
            if intro and len(intro) > 40:
                sections.append(intro)
            elif intro and heading_sections:
                heading_sections[0] = f"{intro}\n\n{heading_sections[0]}"

            sections.extend(heading_sections)

        index = 0
        for section in sections:
            if not section:
                continue
            if len(section) <= config.CHUNK_SIZE:
                chunks.append(
                    Chunk(
                        text=section,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
            else:
                start = 0
                while start < len(section):
                    piece = section[start : start + config.CHUNK_SIZE].strip()
                    if piece:
                        chunks.append(
                            Chunk(
                                text=piece,
                                source=doc.source,
                                index=index,
                                produced_by="chunker.py::split_documents",
                            )
                        )
                        index += 1
                    start += config.CHUNK_SIZE - config.CHUNK_OVERLAP

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
