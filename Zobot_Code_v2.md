# TechAtlas v2 Zobot Code (Deluge)

**Backend URL**: `https://techatlas-production.up.railway.app`

## 1. Message Handler
*Paste this into the "Message Handler" section.*

```javascript
// 1. Check if tracking is enabled for this chat
is_tracking = zoho.cliq.getDb("tracking_" + chat.get("id"));

// Default to false if not set
if(is_tracking == null || is_tracking != "true")
{
	return Map();
}

// 2. Prepare payload for detection
payload = Map();
payload.put("message", message);

// 3. Call TechAtlas Backend
response = invokeurl
[
	url : "https://techatlas-production.up.railway.app/detect-decision"
	type : POST
	parameters : payload.toString()
	headers : {"Content-Type":"application/json"}
];

// 4. Check confidence score (Strict > 0.8)
if(response.get("is_decision") == true && response.get("confidence") > 0.8)
{
	// NOTE: Backend returns 'suggested_title', not 'title'
	title = response.get("suggested_title");
	
	// Create a card
	card = Map();
	card.put("title", "🧠 Decision Detected");
	card.put("theme", "modern-inline");
	
	text = "I noticed a potential decision: *" + title + "*\n\nWould you like to save this to the TechAtlas Knowledge Base?";
	
	// Buttons
	buttons = List();
	
	// Save Button
	save_btn = Map();
	save_btn.put("label", "Save & Analyze");
	save_btn.put("type", "+");
	save_btn.put("action", Map());
	save_btn.get("action").put("type", "invoke.function");
	save_btn.get("action").put("name", "save_decision_fn"); 
	save_btn.get("action").put("data", {"title": title, "message": message, "user": user.get("email")});
	buttons.add(save_btn);
	
	// Ignore Button
	ignore_btn = Map();
	ignore_btn.put("label", "Ignore");
	ignore_btn.put("type", "-");
	ignore_btn.put("action", Map());
	ignore_btn.get("action").put("type", "invoke.function");
	ignore_btn.get("action").put("name", "ignore_fn");
	buttons.add(ignore_btn);
	
	return {"text": text, "card": card, "buttons": buttons};
}

// If not a decision or low confidence, ignore silently
return Map();
```

## 2. Command Handler
*Paste this into the "Command Handler" section.*

```javascript
// Command: /start, /stop, /ask
command_name = command.get("name");

if(command_name == "start")
{
	// Enable tracking
	zoho.cliq.saveDb("tracking_" + chat.get("id"), "true");
	return "🟢 **TechAtlas Tracking Enabled.** I will now monitor this chat for decisions.";
}
else if(command_name == "stop")
{
	// Disable tracking
	zoho.cliq.saveDb("tracking_" + chat.get("id"), "false");
	return "🔴 **TechAtlas Tracking Paused.** I will stop monitoring this chat.";
}
else if(command_name == "ask")
{
	// RAG Query (Works regardless of tracking state)
	query = params.get("arguments");
	
	if(query == null || query == "")
	{
		return "Please provide a question. Example: `/ask Why did we choose Postgres?`";
	}
	
	response = invokeurl
	[
		url : "https://techatlas-production.up.railway.app/query-decisions"
		type : POST
		parameters : {"query": query, "user": user.get("email")}.toString()
		headers : {"Content-Type":"application/json"}
	];
	
	answer = response.get("answer");
	sources = response.get("sources");
	
	text = "🤖 **TechAtlas Answer:**\n" + answer + "\n\n**Sources:**";
	for each source in sources
	{
		text = text + "\n- " + source.get("title") + " (Score: " + source.get("relevance_score") + ")";
	}
	
	return text;
}

return "Unknown command.";
```

## 3. Functions (Execution Logic)
*Create these as separate Functions in the Zobot editor.*

### Function: `save_decision_fn`
```javascript
title = arguments.get("title");
message_text = arguments.get("message");
user_email = arguments.get("user");

// 1. Analyze first
analysis_response = invokeurl
[
	url : "https://techatlas-production.up.railway.app/analyze-decision"
	type : POST
	parameters : {"title": title, "rationale": message_text}.toString()
	headers : {"Content-Type":"application/json"}
];

score = analysis_response.get("analysis").get("feasibility_score");

// 2. Save decision
save_payload = Map();
save_payload.put("title", title);
save_payload.put("owner", user_email);
save_payload.put("rationale", message_text);
save_payload.put("due_date", zoho.currentdate.addDay(7));
save_payload.put("thread_link", "https://cliq.zoho.com");

save_response = invokeurl
[
	url : "https://techatlas-production.up.railway.app/save-decision"
	type : POST
	parameters : save_payload.toString()
	headers : {"Content-Type":"application/json"}
];

if(save_response.get("success") == true)
{
	return "✅ **Saved!**\nFeasibility Score: " + score + "/100\nAdded to Knowledge Base.";
}
else
{
	return "❌ Failed to save decision. Please try again.";
}
```

### Function: `ignore_fn`
```javascript
return "Okay, I'll ignore this.";
```
