document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("email-gen-form");
  const resultArea = document.getElementById("result-area");

  let lastFeedbackData = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await generateOrRegenerate();
  });

  async function generateOrRegenerate(regenPayload = null) {
    resultArea.innerHTML = "<em>Generating…</em>";

    let payload;

    if (regenPayload) {
      payload = { ...regenPayload };
    } else {
      const contextPoints = [
        form.context_point_1.value.trim(),
        form.context_point_2.value.trim(),
        form.context_point_3.value.trim(),
      ];

      const optional = form.optional_context.value.trim();
      if (optional) contextPoints.push(optional);

      payload = {
        company_name: form.company_name.value.trim(),
        industry: form.industry.value.trim(),
        tone: form.tone.value,
        focus: form.focus.value,
        additional_context: contextPoints,
        model_choice: form.model_choice.value,
      };
    }

    payload.user_id = '123345-123345-8234';

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

      const response = await res.json();

      const {
        message,
        prompt_version,
        message_id,
        parent_message_id,
        prompt_text
      } = response;

      lastFeedbackData = {
        message_id,
        parent_message_id: parent_message_id || payload.parent_message_id || null,
        feedback_type: null,
        company_name: payload.company_name,
        industry: payload.industry,
        tone: payload.tone,
        focus: payload.focus,
        context: payload.context || (payload.additional_context || []).join(" "),
        model_used: payload.model_choice,
        prompt_template: prompt_version,
        prompt_text: prompt_text || "",
        generated_message: {
          message: message,
          generated_at: new Date().toISOString()
        }
      };

      resultArea.innerHTML = `
        <h2>Generated Email</h2>
        <pre>${message}</pre>
        <button id="upvote">👍 Upvote</button>
        <button id="downvote">👎 Downvote</button>
        <button id="regenerate">🔄 Regenerate</button>
      `;

      document.getElementById("upvote").onclick = () => sendFeedback("upvote");
      document.getElementById("downvote").onclick = () => sendFeedback("downvote");

      document.getElementById("regenerate").onclick = () => {
        const regenPayload = {
          company_name: payload.company_name,
          industry: payload.industry,
          tone: payload.tone,
          focus: payload.focus,
          context: payload.context || (payload.additional_context || []).join(" "),
          model_choice: payload.model_choice,
          parent_message_id: message_id   // KEY for regeneration
        };
        generateOrRegenerate(regenPayload);
      };

    } catch (err) {
      resultArea.innerHTML = `<p style="color: red;">Error: ${err.message}</p>`;
    }
  }

  async function sendFeedback(type) {
    if (!lastFeedbackData) return;

    const feedbackPayload = {
      ...lastFeedbackData,
      feedback_type: type,
      user_id: '123345-123345-8234'
    };

    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedbackPayload)
    });

    await res.json();
    alert("Thanks for your feedback!");
  }
});
