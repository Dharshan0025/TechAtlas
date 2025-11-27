# TechAtlas Zobot Code (Deluge)

**Backend URL**: `https://techatlas-production.up.railway.app`

## 1. Message Handler
*Paste this into the "Message Handler" section of your Zobot.*

```javascript
// Check if the bot is active for this chat
is_active = zoho.cliq.getDb("is_active_" + chat.get("id"));

if(is_active == "true")
{
	// Prepare payload for detection
	payload = Map();
	payload.put("message", message);
	
	// Call TechAtlas Backend
	response = invokeurl
	[
		url : "https://techatlas-production.up.railway.app/detect-decision"
		type : POST
		parameters : payload.toString()
		headers : {"Content-Type":"application/json"}
	];
	
	// Parse response
	if(response.get("is_decision") == true && response.get("confidence") > 0.7)
	{
		title = response.get("title");
		
		// Create a card
		card = Map();
		card.put("title", "🧠 Decision Detected");
		card.put("theme", "modern-inline");
		
		// Card Text
		text = "I noticed a potential decision: *" + title + "*\n\nWould you like to save this to the TechAtlas Knowledge Base?";
		
		// Buttons
		buttons = List();
		
		// Save Button
		save_btn = Map();
		save_btn.put("label", "Save & Analyze");
		save_btn.put("type", "+");
		save_btn.put("action", Map());
		save_btn.get("action").put("type", "invoke.function");
		save_btn.get("action").put("name", "save_decision_action"); 
		save_btn.get("action").put("data", {"title": title, "message": message, "user": user.get("email")});
		buttons.add(save_btn);
		
		// Ignore Button
		ignore_btn = Map();
		ignore_btn.put("label", "Ignore");
		ignore_btn.put("type", "-");
		ignore_btn.put("action", Map());
		ignore_btn.get("action").put("type", "invoke.function");
		ignore_btn.get("action").put("name", "ignore_action");
		buttons.add(ignore_btn);
		
		return {"text": text, "card": card, "buttons": buttons};
	}
}

return Map();
```

## 2. Command Handler
*Paste this into the "Command Handler" section.*

```javascript
// Command: /start, /stop, /ask, /analyze
command_name = command.get("name");

if(command_name == "start")
{
	// Enable passive listening
	zoho.cliq.saveDb("is_active_" + chat.get("id"), "true");
	return "🟢 **TechAtlas is now listening.** I will notify you when I detect a decision.";
}
else if(command_name == "stop")
{
	// Disable passive listening
	zoho.cliq.saveDb("is_active_" + chat.get("id"), "false");
	return "🔴 **TechAtlas is paused.** I will no longer interrupt your conversation.";
}
else if(command_name == "ask")
{
	// RAG Query
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
	
	// Format response
	text = "🤖 **TechAtlas Answer:**\n" + answer + "\n\n**Sources:**";
	for each source in sources
	{
		text = text + "\n- " + source.get("title") + " (Score: " + source.get("relevance_score") + ")";
	}
	
	return text;
}

return "Unknown command.";
```

## 3. Execution Handler
*Paste this into the "Execution Handler" section.*

```javascript
action_name = params.get("name");
data = params.get("arguments");

if(action_name == "save_decision_action")
{
	title = data.get("title");
	message_text = data.get("message");
	user_email = data.get("user");
	
	// 1. Analyze first to get feasibility
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
	save_payload.put("due_date", zoho.currentdate.addDay(7)); // Default 1 week
	save_payload.put("thread_link", "https://cliq.zoho.com"); // Placeholder
	
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
}
else if(action_name == "ignore_action")
{
	return "Okay, I'll ignore this.";
}

return Map();
```
