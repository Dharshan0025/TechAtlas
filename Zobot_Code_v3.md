# TechAtlas v3 Zobot Code (Deluge)

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
payload.put("user", user.get("email"));
payload.put("channel_id", chat.get("id"));

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
	title = response.get("suggested_title");
	
	// AUTO-SAVE LOGIC
	save_payload = Map();
	save_payload.put("title", title);
	save_payload.put("owner", user.get("email"));
	save_payload.put("rationale", message);
	save_payload.put("due_date", zoho.currentdate.addDay(7));
	save_payload.put("thread_link", "https://cliq.zoho.com"); // Placeholder
	save_payload.put("channel_id", chat.get("id"));

	save_response = invokeurl
	[
		url : "https://techatlas-production.up.railway.app/save-decision"
		type : POST
		parameters : save_payload.toString()
		headers : {"Content-Type":"application/json"}
	];
	
	if(save_response.get("success") == true)
	{
		decision_id = save_response.get("decision_id");
		
		// Create a card
		card = Map();
		card.put("title", "🧠 Decision Detected & Saved");
		card.put("theme", "modern-inline");
		
		text = "I detected a decision: *" + title + "*\nIt has been automatically saved to the TechAtlas Knowledge Base.";
		
		// Buttons
		buttons = List();
		
		// Analyze Button
		analyze_btn = Map();
		analyze_btn.put("label", "🔍 Analyze Risks");
		analyze_btn.put("type", "+");
		analyze_btn.put("action", Map());
		analyze_btn.get("action").put("type", "invoke.function");
		analyze_btn.get("action").put("name", "analyze_decision_fn"); 
		analyze_btn.get("action").put("data", {"decision_id": decision_id});
		buttons.add(analyze_btn);
		
		return {"text": text, "card": card, "buttons": buttons};
	}
}

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

### Function: `analyze_decision_fn`
```javascript
decision_id = arguments.get("decision_id");

// Call backend to analyze
analysis_response = invokeurl
[
	url : "https://techatlas-production.up.railway.app/decisions/" + decision_id + "/analyze"
	type : POST
	headers : {"Content-Type":"application/json"}
];

if(analysis_response.get("success") == true)
{
	analysis = analysis_response.get("analysis");
	score = analysis.get("feasibility_score");
	risk = analysis.get("risk_level");
	recommendation = analysis.get("recommendation");
	
	// Format response
	text = "📊 **Analysis Result**\n\n";
	text = text + "**Feasibility Score:** " + score + "/100\n";
	text = text + "**Risk Level:** " + risk + "\n";
	text = text + "**Recommendation:** " + recommendation + "\n\n";
	
	text = text + "[View Full Dashboard](https://techatlas-dashboard.up.railway.app/decisions/" + decision_id + ")";
	
	return text;
}
else
{
	return "❌ Analysis failed. Please try again later.";
}
```
