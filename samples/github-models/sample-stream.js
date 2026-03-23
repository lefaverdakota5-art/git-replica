/**
 * sample-stream.js — GitHub Models chat completion with streaming.
 *
 * Prerequisites
 * -------------
 * 1. Create a GitHub personal access token (classic or fine-grained).
 * 2. Export it before running:
 *      bash/zsh :  export GITHUB_TOKEN="ghp_…"
 *      PowerShell: $Env:GITHUB_TOKEN="ghp_…"
 *      cmd.exe  :  set GITHUB_TOKEN=ghp_…
 * 3. Run:  npm install && node sample-stream.js
 *
 * External models
 * ---------------
 * If you have external models configured, reference them as:
 *   custom/<key_id>/<model_id>
 */

import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";
import { createSseStream } from "@azure/core-sse";

const token = process.env["GITHUB_TOKEN"];
if (!token) {
  console.error(
    "Error: GITHUB_TOKEN environment variable is not set.\n" +
      "Set it before running this script:\n" +
      '  export GITHUB_TOKEN="YOUR-GITHUB-TOKEN-GOES-HERE"'
  );
  process.exit(1);
}

const endpoint = "https://models.github.ai/inference";

/**
 * Replace with any model available to your account on GitHub Models, e.g.:
 *   "openai/gpt-4o"
 *   "openai/gpt-4o-mini"
 *   "meta/Llama-3.3-70B-Instruct"
 *   "custom/<key_id>/<model_id>"  ← for external / bring-your-own-key models
 */
const model = "openai/gpt-4o";

export async function main() {
  const client = ModelClient(endpoint, new AzureKeyCredential(token));

  const response = await client.path("/chat/completions").post({
    body: {
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: "Give me 5 good reasons to learn TypeScript." },
      ],
      model,
      temperature: 1.0,
      top_p: 1.0,
      max_tokens: 1000,
      stream: true,
    },
  });

  if (isUnexpected(response)) {
    throw new Error(
      `Unexpected response (${response.status}): ${JSON.stringify(response.body.error)}`
    );
  }

  const stream = createSseStream(response.asBrowserStream());

  process.stdout.write("Assistant: ");
  for await (const event of stream) {
    if (event.data === "[DONE]") {
      break;
    }
    const parsed = JSON.parse(event.data);
    const delta = parsed.choices?.[0]?.delta?.content;
    if (delta) {
      process.stdout.write(delta);
    }
  }
  process.stdout.write("\n");
}

main().catch((err) => {
  console.error("The sample encountered an error:", err);
  process.exit(1);
});
