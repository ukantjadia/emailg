document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("email-gen-form");
  const resultArea = document.getElementById("result-area");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = "<em>Generating…</em>";

    // required context points
    const contextPoints = [
      form.context_point_1.value.trim(),
      form.context_point_2.value.trim(),
      form.context_point_3.value.trim(),
    ];

    // optional
    const optional = form.optional_context.value.trim();

    const payload = {
      company_name: form.company_name.value.trim(),
      industry: form.industry.value.trim(),
      tone: form.tone.value,
      focus: form.focus.value,
      additional_context: contextPoints,
      model_choice: form.model_choice.value,
      // only include if user entered something
      ...(optional && { optional_context: optional })
    };

    try {
      const res = await fetch("/api/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || res.statusText);
      }

      const { message, prompt_version } = await res.json();

      resultArea.innerHTML = `
        <h2>Generated Email</h2>
        <pre>${message}</pre>
        <p><small>Prompt version: ${prompt_version}</small></p>
        <button id="upvote">👍 Upvote</button>
        <button id="downvote">👎 Downvote</button>
        <button id="regenerate">🔄 Regenerate</button>
      `;

      document.getElementById("upvote")
        .onclick = () => sendFeedback({ is_upvote: true });
      document.getElementById("downvote")
        .onclick = () => sendFeedback({ is_downvote: true });
      document.getElementById("regenerate")
        .onclick = () => form.requestSubmit();

    } catch (err) {
      resultArea.innerHTML =
        `<p style="color: red;">Error: ${err.message}</p>`;
    }
  });

  async function sendFeedback(flags) {
    const feedbackPayload = {
      ...flags,
      // TODO: attach lead_id, user_id, etc. if you have them
    };

    await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedbackPayload)
    });
    alert("Thanks for your feedback!");
  }
});
