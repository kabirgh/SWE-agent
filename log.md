## Run commands

sweagent run-batch \
    --instances.type file \
    --instances.path /root/SWE-agent/instances.jsonl \
    --instances.shuffle=False \
    --config config/ml_claude37.yaml \
    --num_workers=3

Updated after pulling latest main 17/03/2025.
instances.jsonl no longer needs id. instance_id is now used instead.
name and output tokens set in config.

---

sweagent run-batch \
    --instances.type file \
    --instances.path /root/SWE-agent/instances.jsonl \
    --instances.shuffle=False \
    --config config/claude37.yaml \
    --agent.model.name claude-3-7-sonnet-20250219 \
    --agent.model.per_instance_cost_limit=1.50

(Same command as below)
instances.jsonl must contain:
- repo_name: "testbed"
- id: $instance_id
- image_name: $local_docker_image_name

---

sweagent run-batch \
    --instances.type file \
    --instances.path /root/SWE-agent/instances.jsonl \
    --instances.shuffle=False \
    --config config/claude37.yaml \
    --agent.model.name claude-3-7-sonnet-20250219
    --agent.model.per_instance_cost_limit=1.50

Failed because `submit` tool call requires agent to be in root of repo but it had cd into /testbed and didn't know to cd out.
```log
2025-03-15 17:32:16,813 - INFO - swea-agent - ========================= STEP 51 =========================
2025-03-15 17:32:16,821 - DEBUG - swea-lm - n_cache_control: 2
2025-03-15 17:32:16,847 - DEBUG - swea-lm - About to call litellm
2025-03-15 17:32:18,589 - DEBUG - swea-lm - Litellm call successful
2025-03-15 17:32:18,604 - INFO - swea-lm - Response: ModelResponse(id='chatcmpl-7eedf0fa-a41f-419b-9521-e5d99bfbc2a3', created=1742059938, model='claude-3-7-sonnet-20250219', object='chat.completion', system_fingerprint=None, choices=[Choices(finish_reason='tool_calls', index=0, message=Message(content='I apologize for the confusion. Let me submit the changes properly:', role='assistant', tool_calls=[ChatCompletionMessageToolCall(index=1, function=Function(arguments='{}', name='submit'), id='toolu_011eUcr3vXhCktcTzWNn1VUD', type='function')], function_call=None, provider_specific_fields={'citations': None, 'thinking_blocks': None}))], usage=Usage(completion_tokens=50, prompt_tokens=23291, total_tokens=23341, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetailsWrapper(audio_tokens=None, cached_tokens=23148, text_tokens=None, image_tokens=None), cache_creation_input_tokens=143, cache_read_input_tokens=23148))
2025-03-15 17:32:18,635 - DEBUG - swea-lm - input_tokens=69, output_tokens=13, instance_cost=0.54, cost=0.01
2025-03-15 17:32:18,641 - DEBUG - swea-lm - total_tokens_sent=12,788, total_tokens_received=2,001, total_cost=0.54, total_api_calls=51
2025-03-15 17:32:18,647 - INFO - swea-agent - 💭 THOUGHT
I apologize for the confusion. Let me submit the changes properly:

🎬 ACTION
submit
2025-03-15 17:32:18,653 - TRACE - swea-env - Input:
submit
2025-03-15 17:32:18,866 - TRACE - swea-env - Output:
Traceback (most recent call last):
  File "/root/tools/review_on_submit_m/bin/submit", line 54, in <module>
    main()
  File "/root/tools/review_on_submit_m/bin/submit", line 19, in main
    assert repo_root
AssertionError
2025-03-15 17:32:18,867 - TRACE - swea-env - Input:
_state_anthropic
2025-03-15 17:32:19,074 - TRACE - swea-env - Output:

2025-03-15 17:32:19,085 - DEBUG - swea-tools - Retrieved state from environment: {'working_dir': '/testbed'}
2025-03-15 17:32:19,100 - INFO - swea-agent - 🤖 MODEL INPUT
OBSERVATION:
Traceback (most recent call last):
  File "/root/tools/review_on_submit_m/bin/submit", line 54, in <module>
    main()
  File "/root/tools/review_on_submit_m/bin/submit", line 19, in main
    assert repo_root
AssertionError
```

---

sweagent run-batch \
    --instances.type file \
    --instances.path /root/SWE-agent/instances.jsonl \
    --instances.shuffle=False \
    --config config/default.yaml \
    --agent.model.name claude-3-7-sonnet-20250219

Failed because `max_tokens: 128000 > 64000, which is the maximum allowed number of output tokens for claude-3-7-sonnet-20250219`

---

sweagent run-batch \
    --instances.type swe_bench \
    --instances.subset multi \
    --instances.split test \
    --instances.slice :5 \
    --instances.shuffle=False \
    --config config/default.yaml \
    --agent.model.name claude-3-7-sonnet-20250219

Failed because tried to pull non-existent docker image

## Env vars
python not found, pip not found, javac not found, etc

swe-rex process doesn't inherit docker env vars (see https://github.com/SWE-agent/SWE-ReX/issues/185)
Workaround: tools/ml_setup/install.sh reads env vars from /proc/1/environ and adds them to the env.
