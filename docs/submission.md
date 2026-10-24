# Builder Center submission draft

Status: do not submit as a completed demonstration until live AWS verification
and a public video are available. Confirm eligibility of a newly built agent.

## Title

Bousbi Remembers: One S3 Tool Gives a Storytelling Agent Its Previous Chapter

## Description

A bedtime-story agent gains one read-only tool to retrieve a previous chapter from Amazon S3. The project compares the same Amazon Bedrock agent with and without retrieval, exploring how tool access can support consistent characters and story continuity.

## Body

### The missing capability

A storyteller can invent a new adventure, but continuing a particular saved story
requires access to what actually happened. This project explores that gap with a
small Amazon Bedrock agent and one new tool.

### The starting point

The baseline is a newly built Bedrock Converse storyteller with no retrieval tool.
It can respond to story prompts but has no access to previous chapters. It was
created during this challenge, inspired by Bousbi's Tiny Tale Machine, an earlier
template-based serverless app. That earlier app was not an agent.

### One new tool

`get_previous_story(story_id)` reads a UTF-8 chapter from a fixed prefix in a private
Amazon S3 bucket. The model requests the tool; the Python runner retrieves the
chapter and sends the result back through the Bedrock Converse tool-result protocol.

The tool accepts a story ID, never an arbitrary bucket or URL. It restricts IDs,
caps the returned file at 16 KiB, closes response streams, and returns errors to
the model if retrieval fails. The agent loop is limited to four model calls.

### The comparison

Both modes receive the same request: continue the saved story `moon-garden`.
Without retrieval, the intended behavior is to ask for the missing chapter.
With retrieval, the intended behavior is to retrieve the chapter and continue
Nia and Pip's adventure while preserving its characters and unfinished events.

### Verification status

The implementation includes offline tests for dispatch, tool-result IDs, retrieval
limits, rejected inputs, disabled tools, and loop bounds. Live Bedrock/S3 behavior
and story quality still require verification. This write-up does not claim a
successful AWS demonstration yet.

### Why it is useful

The same read-only retrieval pattern can help an agent use a saved project brief,
support note, or previous lesson. A small, explicit tool gives the model access to
information it otherwise cannot know.

### Costs

Bedrock inference and S3 requests/storage may incur charges. This CLI implementation
does not require an always-running server. Model access and pricing should be
checked before running it.

## Tags

serverless, amazon-bedrock, amazon-s3, ai-agents, python

## GitHub or GitLab Repository

https://github.com/mtzanida/bousbi-remembers

## Endpoint or live demo

Pending: public video under 3 minutes showing the actual before/after execution.
The challenge requests a video in the demo field; add the same video link in the
body if this form exposes only Endpoint or live demo. Do not use a fabricated URL.

## Jupyter or SageMaker notebook

Leave empty; this project does not require a notebook.
