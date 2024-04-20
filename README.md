The libraries you need are exa-py and openai.

This program is going to use EXA as a search engine and then use the results to generate a response to the user's question. It limits the story size to 1000 characters and it basicall calls for 5 articles the way it works now.It lets GPT to decide if it want to make a function call or not. In this exampel it only has one function that it is calling.

THere is no user interface.
I just used an example from the openai cookbook and modified it.
The big learning for me was that openai says that to use a function with GPT you need to call the function. What this means to me is that if you want the program to run after you input the question to gpt-3.5 or whatever model you want you will actually need to help gpt by calling the specific function that GPT want to use. As an example the following bit of code will return tool calling information

response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=messages,
      tools=tools,
      tool_choice="auto",
  )
  response_message = response.choices[0].message
  tool_calls = response_message.tool_calls
 
Now when tool_calls has something in it you can run a line of code like this "if tool_calls:" and start actually calling the tool.

(One note is if you actually plug your function into tool.choice line it will actually call the tool and you won't have to do anything more. Also if you put none in instead of auto it won't call any tool at all)
  
