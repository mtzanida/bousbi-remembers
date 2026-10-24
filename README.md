# Bousbi Remembers

One new tool gives a bedtime-story agent access to its previous chapter.

**Status:** implementation and offline protocol tests only. No AWS deployment,
live Bedrock inference, public video or challenge submission has been completed.
This is a new agent built during the challenge, inspired by an older template-based
storytelling app. The older app was not an AI agent. Confirm eligibility with the
organizers before entering a challenge that requires a previously built agent.

## Before and after

Both modes use the same Bedrock model, system prompt and user request.
`before` exposes no retrieval tool. `after` exposes exactly one tool:
`get_previous_story(story_id)`. The model chooses whether to request it; Python
dispatches the request, reads a private S3 object and returns the result using
the matching Bedrock `toolUseId`. The model then writes a continuation.

Expected behavior, to verify in a live run:

| Mode | Expected result |
|---|---|
| Before | Requests the missing prior chapter rather than pretending to remember |
| After | Retrieves moon-garden from S3 and continues Nia and Pip's golden-seed adventure |

No AWS calls are mocked in the application. The unit tests use explicit fake
clients and do not establish model quality or AWS integration success.

## Run locally with AWS

Requirements: Python 3.11+, AWS CLI configured with an authorized profile, an AWS
account with Bedrock access, and a Converse-compatible model supporting tool use.
Choose the model ID and Region from your account; model availability and charges vary.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=your-accessible-tool-capable-model-id
export STORY_BUCKET=your-globally-unique-private-bucket-name
```

Create the sample bucket in us-east-1 using a provisioning identity with permission
to create/configure it. The runtime identity only needs the read permissions below.

```bash
aws s3api create-bucket --bucket "$STORY_BUCKET" --region us-east-1
aws s3api put-public-access-block --bucket "$STORY_BUCKET" --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-encryption --bucket "$STORY_BUCKET" --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws s3 cp sample_data/moon-garden.txt "s3://$STORY_BUCKET/stories/moon-garden.txt"
python agent.py --mode before
python agent.py --mode after
```

The bucket creation example is specifically for us-east-1. Other Regions require
the corresponding CreateBucketConfiguration. No web server, NAT gateway, database
or public S3 bucket is needed. This is a CLI agent, not a hosted web app.

## Permissions

Adapt `docs/runtime-policy.json`: restrict `s3:GetObject` to the story prefix and
`bedrock:InvokeModel` to the exact model ARN. If using an inference profile, include
the profile and the underlying model ARNs required by its routing configuration.
Use temporary AWS credentials, not access keys committed to the repository.

## Verification

```bash
python -m unittest discover -s tests -v
```

For the live demo, look for the actual `[tool] ... retrieved from S3` trace. Check
that Nia, Pip, the golden seed, green pouch and pond remain consistent. Rerun with
a nonexistent story ID: the agent should explain retrieval failed. Test a normal
new-story request too; it should not need a saved chapter. A model can ignore an
instruction or request an unnecessary tool: record actual behavior, not a scripted
success claim. Four model calls and 650 output tokens per call bound each run's
loop, but do not guarantee a dollar cost ceiling.

## Costs and cleanup

Bedrock inference and S3 storage/requests may be billed; do not assume free-tier
coverage. Verify pricing and credits for your selected model before executing.
The CLI performs no calls while idle and creates no recurring background jobs.
Keep only synthetic stories in the demo bucket. Retrieved text is treated as
untrusted data in the system prompt, though prompting alone cannot guarantee
resistance to prompt injection. Tool execution is read-only and prefix-restricted.

After recording, remove the demo object and empty demo bucket you created:

```bash
aws s3 rm "s3://$STORY_BUCKET/stories/moon-garden.txt"
aws s3api delete-bucket --bucket "$STORY_BUCKET"
```

Do not use these commands on a shared bucket. Remove any dedicated IAM policy/role
you created separately. See `docs/submission.md` and `docs/demo-script.md` for the
submission draft and recording plan.

## References

- [Bedrock client-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html)
- [Boto3 Converse](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/converse.html)
- [Challenge](https://builder.aws.com/build/hackathons/2e275689-b202-316e-93b8-10cd6d6d1e4a/weekend-challenge-give-your-agent-a-tool)
