document.addEventListener("DOMContentLoaded", () => {
  console.log("[email_generator.js] DOMContentLoaded");
  const form = document.getElementById("email-gen-form");
  const resultArea = document.getElementById("result-area");

  // Store last generation data for feedback
  let lastFeedbackData = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("[email_generator.js] Form submitted");
    await generateOrRegenerate();
  });

  async function generateOrRegenerate(regenPayload = null) {
    resultArea.innerHTML = "<em>Generating…</em>";
    let payload, endpoint;
    if (regenPayload) {
      payload = { ...regenPayload };
      if (payload.additional_context) {
        payload.context = payload.additional_context.join(" ");
        delete payload.additional_context;
      }
      // If context already exists, leave it as is
      endpoint = "/regenerate";
      console.log("[email_generator.js] Regeneration payload:", payload);
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
      if (form.parent_message_id) {
        payload.parent_message_id = form.parent_message_id;
      }
      endpoint = "/api/generate-email";
      console.log("[email_generator.js] Generation payload:", payload);
    }
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      console.log(`[email_generator.js] ${endpoint} response status:`, res.status);
      if (!res.ok) {
        const err = await res.json();
        console.error("[email_generator.js] Error response:", err);
        throw new Error(err.error || res.statusText);
      }
      const { message, prompt_version, message_id, parent_message_id, prompt_text } = await res.json();
      console.log("[email_generator.js] API response:", { message, prompt_version, message_id, parent_message_id, prompt_text });
      lastFeedbackData = {
        message_id,
        parent_message_id: parent_message_id || payload.parent_message_id || null,
        feedback_type: null, // will be set on upvote/downvote
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
        <p><small>Prompt version: ${prompt_version}</small></p>
        <button id="upvote">👍 Upvote</button>
        <button id="downvote">👎 Downvote</button>
        <button id="regenerate">🔄 Regenerate</button>
      `;
      console.log("[email_generator.js] Result area updated");
      document.getElementById("upvote")
        .onclick = () => sendFeedback("upvote");
      document.getElementById("downvote")
        .onclick = () => sendFeedback("downvote");
      document.getElementById("regenerate")
        .onclick = () => {
          form.parent_message_id = message_id;
          const nextRegenPayload = {
            company_name: payload.company_name,
            industry: payload.industry,
            tone: payload.tone,
            focus: payload.focus,
            context: payload.context || (payload.additional_context || []).join(" "),
            model_choice: payload.model_choice,
            parent_message_id: message_id
          };
          generateOrRegenerate(nextRegenPayload);
        };
    } catch (err) {
      resultArea.innerHTML = `<p style="color: red;">Error: ${err.message}</p>`;
      console.error("[email_generator.js] Exception:", err);
    }
  }

  async function sendFeedback(type) {
    if (!lastFeedbackData) return;
    const feedbackPayload = {
      ...lastFeedbackData,
      feedback_type: type
    };
    // Remove user_id from requiredFields check
    const requiredFields = [
      'message_id', 'company_name', 'industry', 'tone', 'focus', 'context',
      'model_used', 'prompt_template', 'prompt_text', 'generated_message', 'feedback_type'
    ];
    for (const field of requiredFields) {
      if (typeof feedbackPayload[field] === 'undefined') {
        alert(`Missing required feedback field: ${field}`);
        return;
      }
    }
    console.log("[email_generator.js] Sending feedback:", feedbackPayload);
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedbackPayload)
    });
    const result = await res.json();
    console.log("[email_generator.js] Feedback API response:", result);
    alert("Thanks for your feedback!");
  }

  // async function regenerateWithParent(regenPayload) {
  //   const res = await fetch("/regenerate", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify(regenPayload)
  //   });
  //   // ... handle response as before ...
  // }
});
