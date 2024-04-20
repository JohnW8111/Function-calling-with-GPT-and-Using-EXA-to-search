#this program is going to use EXA as a search engine and then use the results to generate a response to the user's question. It limits the story size to 1000 characters and it basicall calls for 5 articles the way it works now.It lets GPT to decide if it want to make a function call or not. In this exampel it only has one function that it is calling

import openai
import os
import sys
import json
from exa_py import Exa
import requests

openai.api_key = os.environ['OPENAI_API_KEY']
my_secret = os.environ['EXA_API_KEY']
exa = Exa(my_secret)

client = openai.OpenAI()


def fetch_results(question,number):
  # if you want to control the questions better you can change where you get the question from and the number from. Otherwise it will use the intiall question and arbitralrily stick a 5 in fro the number
  """question = input(
      "What is your question? Remember to put this into the form of a statement with a colon at the end:\n"
  )
  number = int(input("The number of search results up to 10:\n"))"""

  url = "https://api.exa.ai/search"

  payload = {
      "contents": {
          "text": {
              "maxCharacters": 1000,
              "includeHtmlTags": False
          }
      },
      "query": question,
      "useAutoprompt": True,
      "type": "neural",
      "numResults":number, 
      "startPublishedDate": "\"2023-11-01\""
  }
  headers = {
      "accept": "application/json",
      "content-type": "application/json",
      "x-api-key": "23588e3d-28e8-464c-afd6-b9cddd68f10e"
  }

  response = requests.post(url, json=payload, headers=headers)

  content = str(response.json())
  #print(content)
  """if response.status_code == 200:
      content = response.json()
      if 'results' in content and isinstance(content['results'], list):
          for result in content['results']:
              print(result['text'] if 'text' in result else "No text available")
  else:
      print("Failed to fetch results. Status Code:", response.status_code)"""

  return content
  


# Note: This code assumes that the `results` variable is either a list or a similar iterable of dictionaries.
# You might need to adjust the list comprehension according to the actual structure of `results`.
def run_conversation():
  # Step 1: send the conversation and available functions to the model
  content = input(
      'What is your question? Remember to put this into the form of a statement with a colon at the end.'
      + '\n')
  messages = [{"role": "user", "content": content}]
  tools = [{
      "type": "function",
      "function": {
          "name": "fetch_results",
          "description":
          "Search and retrieve content based on a user question",
          "parameters": {
              "type": "object",
              "properties": {
                  "question": {
                      "type":
                      "string",
                      "description":
                      "Question phrased as a statement with a colon",
                  },
                  "number": {
                      "type": "integer",
                      "description": "Number of search results, up to 10"
                  },
              },
              "required": ["question", "number"],
          },
      },
  }]
  response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=messages,
      tools=tools,
      tool_choice="auto",
  )
  response_message = response.choices[0].message
  tool_calls = response_message.tool_calls
  #print(response_message)
  #print(tool_calls)

  # Step 2: check if the model wanted to call a function


  if tool_calls:
    
    available_functions = {
      "fetch_results": fetch_results,
  }
    messages.append(response_message)  # extend conversation with assistant's reply
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        # the next three lines are going to get the question and number to pass to the function  
        args = json.loads(tool_call.function.arguments)
        question = args['question']
        number = args['number']
        # Call the function with the arguments
        function_response = function_to_call(question, number)
      #the next line is where you actually call the function fetch results
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content":function_response,
        })  # extend conversation with function response
  # Step 3: send the final conversation and available functions to the model
    #I added this bit to make sure it summarizes the content it gets from exa search
    summary_request = {
      "role": "system",
      "content": "Please provide a concise summary of all information and responses provided up to this point."
    }
    messages.append(summary_request)
    second_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
    )
    return second_response

# Now we are returning the information from the search and then it was sent to GPT to summarize it
response=run_conversation()
print(response.choices[0].message.content)
