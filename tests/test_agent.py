import io
import unittest
from agent import read_story, run


class S3:
    def __init__(self, data=b'Nia and Pip found a seed.'):
        self.data, self.calls = data, []

    def get_object(self, **kw):
        self.calls.append(kw)
        self.body = io.BytesIO(self.data)
        return {'Body': self.body}


class Runtime:
    def __init__(self, responses):
        self.responses, self.requests = iter(responses), []

    def converse(self, **kw):
        import copy
        self.requests.append(copy.deepcopy(kw))
        return next(self.responses)


def response(content, stop='end_turn'):
    return {'output': {'message': {'role': 'assistant', 'content': content}}, 'stopReason': stop}


class Tests(unittest.TestCase):
    def test_story_scope_and_close(self):
        s3 = S3()
        self.assertIn('Nia', read_story(s3, 'bucket', {'story_id': 'moon-garden'})['story'])
        self.assertEqual(s3.calls, [{'Bucket': 'bucket', 'Key': 'stories/moon-garden.txt'}])
        self.assertTrue(s3.body.closed)

    def test_invalid_inputs_never_reach_s3(self):
        s3 = S3()
        for args in [{'story_id': '../secret'}, {'story_id': 'x', 'bucket': 'other'}, {'story_id': 3}, []]:
            with self.assertRaises(ValueError):
                read_story(s3, 'bucket', args)
        self.assertFalse(s3.calls)

    def test_oversize(self):
        s3 = S3(b'x' * 16385)
        with self.assertRaises(ValueError):
            read_story(s3, 'bucket', {'story_id': 'x'})
        self.assertTrue(s3.body.closed)

    def test_before_no_tools(self):
        runtime = Runtime([response([{'text': 'Please paste the previous story.'}])])
        run(runtime, None, 'model', None, 'continue', enabled=False, emit=lambda _: None)
        self.assertNotIn('toolConfig', runtime.requests[0])

    def test_real_dispatch_protocol(self):
        call = {'toolUse': {'toolUseId': 'id1', 'name': 'get_previous_story', 'input': {'story_id': 'moon-garden'}}}
        runtime = Runtime([response([call], 'tool_use'), response([{'text': 'Continuation'}])])
        s3 = S3()
        run(runtime, s3, 'model', 'bucket', 'continue', emit=lambda _: None)
        result = runtime.requests[1]['messages'][-1]['content'][0]['toolResult']
        self.assertEqual(result['toolUseId'], 'id1')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(s3.calls), 1)

    def test_unknown_tool_denied(self):
        call = {'toolUse': {'toolUseId': 'x', 'name': 'delete_bucket', 'input': {}}}
        runtime = Runtime([response([call], 'tool_use'), response([{'text': 'Unable'}])])
        s3 = S3()
        run(runtime, s3, 'model', 'bucket', 'go', emit=lambda _: None)
        self.assertFalse(s3.calls)
        self.assertEqual(runtime.requests[1]['messages'][-1]['content'][0]['toolResult']['status'], 'error')

    def test_loop_is_bounded(self):
        call = {'toolUse': {'toolUseId': 'x', 'name': 'get_previous_story', 'input': {'story_id': 'x'}}}
        runtime = Runtime([response([call], 'tool_use')] * 4)
        with self.assertRaises(RuntimeError):
            run(runtime, S3(), 'model', 'bucket', 'go', emit=lambda _: None)
        self.assertEqual(len(runtime.requests), 4)


if __name__ == '__main__':
    unittest.main()
