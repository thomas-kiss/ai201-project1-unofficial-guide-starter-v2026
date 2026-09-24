# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

The Unofficial Guide answers questions about `city_guides`, a corpus of 14 travel guides covering nine towns and five topics (eating, walking, regional transport, seasons, accessibility). It retrieves the most relevant sections from those guides for a plain-language question, checks that the match is a confident and then writes a short answer grounded only in what it retrieved (RAG), naming the guide the answer came from. It will not guess when a question falls outside what these guides cover.



## Chunking Strategy

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

**Chunk size:** 900 characters (a safety cap, not the primary rule — see below)
**Overlap:** 120 characters (only used when the cap actually splits a section)

`city_guides` documents aren't split by character count — they're split on
`##` section headings (Getting there, Eating, Where to stay, When to go...).
Reading the guides in Milestone 1 showed each section is written as one
complete, self-contained thought. Measuring it confirmed that: 84 sections
across the 14 guides run 174 to 709 characters (median 295, average 313). A
fixed window either merges two unrelated sections into one chunk or slices
through the middle of one — both make chunks that answer every question a
little and none of them well. Splitting on the heading instead means a chunk
about "eating" never drags in "getting there."

`CHUNK_SIZE` (900) exists only as a cap for a section that runs unusually
long — nothing in this corpus is long enough to trigger it today, but a
future oversized section shouldn't silently become one giant chunk. If the
cap ever fires, `CHUNK_OVERLAP` (120) keeps a sentence at the cut point from
being orphaned between the two pieces.

**I changed my mind partway through.** My first version split on headings but
kept the text before the first heading as its own chunk whenever it existed.
That worked for guides with a real intro paragraph, but four cross-cutting
guides (`guide_walking.md`, `guide_eating.md`, `guide_seasons.md`,
`guide_regional_transport.md`) have no intro at all — just a title line like
`# Walking in the region` — so indexing produced four 23–27 character chunks
that were pure fragments, nothing anyone could answer a question from. I
fixed it by merging any pre-heading text under 40 characters into the first
section instead of emitting it alone. After the fix the shortest chunk in the
corpus is 174 characters (a real section) and the shortest is no longer a
bare title.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

Chunks below are from `python app.py chunks -n 5`, produced by
`chunker.py::split_documents`.

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#5` — produced by: `chunker.py::split_documents`

```
## Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

**Chunk 3** — source: `guide_givens_mill.md#2` — produced by: `chunker.py::split_documents`

```
## Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.
```

**Chunk 4** — source: `guide_kestrelford.md#4` — produced by: `chunker.py::split_documents`

```
## What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

**Chunk 5** — source: `guide_pellew_sands.md#6` — produced by: `chunker.py::split_documents`

```
## When to go

June and September for the beach without the crowds. July and August are busy and the town is at its most itself, for better and worse. Winter is bleak, largely closed, and has a following among people who like that sort of thing.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Do bus tickets work between different companies?

**Answer:**

```
No, bus tickets do not work between different companies; the three regional
operators do not accept each other's tickets.

Source: guide_regional_transport.md
```

This one is worth showing specifically because it's the question that changed
my cutoff. At the starter's default threshold (0.6) the gate refused it. Tehe best
distance was 0.662 - Raising the cutoff to 0.73 let it through without letting any
out-of-scope question in.

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

0.73 (`config.py`, `THRESHOLD`)

I ran my 5 in-corpus questions and the 5 `OUT_OF_SCOPE` questions and recorded
the best (lowest) distance for each:

| Question | In corpus? | Best distance |
|---|---|---|
| Is Halden Bay busy in the summer | Yes | 0.183 |
| What's a short walking path close to Brightwater? | Yes | 0.255 |
| What is the name of the walking route near Kestrelford | Yes | 0.288 |
| What's the best time to visit Brightwater | Yes | 0.354 |
| Do bus tickets work between different companies? | Yes | 0.662 |
| What is the capital of Mongolia? | No | 0.803 |
| How do I write a for loop in Rust? | No | 0.813 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.846 |
| How do I change the oil in a diesel engine? | No | 0.892 |
| Who won the 1994 World Cup? | No | 0.975 |

The two groups separated cleanly: in-corpus topped out at 0.662, out-of-scope
started at 0.803. I put the cutoff at 0.73 — roughly the midpoint of that gap,
closer to the out-of-scope side so a genuinely unrelated question still has
room to be refused even if it happens to share a few words with the corpus.

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

I used AI to pressure test criterion. I used claude to help define a good chunk size/overlap for the chosen corpora as well as to implement the split_documents function. After ID a bug I had it rewrite to merge a short preheading text into the first tection. I also used claude to measure best distances when looking at the relevance cutoffs.

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Chunks stay within one heading's section | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 5. Cited source actually contains the fact | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

Criterion 1 — store.py::search, python app.py ask "..." --show-prompt. For "Is Halden Bay busy in the summer" (expects: "very busy"), the retrieved chunk actually contains it, split across a line wrap in the source:

[from guide_seasons.md]
## Summer, June to August

June is excellent everywhere. July and August split: Halden Bay becomes very
busy and the parking problem dominates, Kestrelford fills with walkers, and
Brightwater goes quiet to the point of dullness with the university empty.

Criterion 2 — real answers from results/run_2026-09-23_1807_before.md, produced by generate.py::answer_from_chunks:

According to guide_seasons.md, late May is arguably the best week of the
year to visit Brightwater because it features long days, everything running,
and the students gone.

No, bus tickets do not work between different companies; the three operators
in the region do not accept each other's tickets (guide_regional_transport.md).

Criterion 3 — run_eval.py::check_out_of_scope, cutoff 0.73:

Out-of-scope questions (the gate should refuse these):
  refused  (best distance 0.803)  What is the capital of Mongolia?
  refused  (best distance 0.892)  How do I change the oil in a diesel engine?
  refused  (best distance 0.975)  Who won the 1994 World Cup?
  refused  (best distance 0.846)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.813)  How do I write a for loop in Rust?
  -> gate refused 5 of 5

Criterion 4 — python app.py chunks -n 5, chunker.py::split_documents:

Chunk 4  |  source: guide_kestrelford.md#4  |  produced by: chunker.py::split_documents
## What to see

The market square on a Saturday morning is the main event and has run
continuously since the 1400s. The parish church has a 13th-century tower you
can climb for £2. The old trackbed walk runs six miles to the next village
along an easy gradient and is the best half-day here.

Criterion 5 — verified by grepping each cited source file for the exact claim the answer attributed to it:

guide_regional_transport.md:16:Three operators run in the region and they do
not accept each other's tickets,

That's the source guide_regional_transport.md cited for "No, bus tickets do
not work between different companies" — the fact is really there.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
